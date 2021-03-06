import json
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.views.generic import TemplateView, View
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import IntegrityError
from django.conf import settings
from growpy.models import Node, Filesystem, Status, OS_CHOICES
from datetime import datetime
from Crypto.Cipher import AES
from Crypto import Random
import base64


class AESCipher:
    def __init__(self, key):
        self.bs = 32
        self.key = key

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]


class Index(TemplateView):

    def dispatch(self, request):
        template = loader.get_template('main.html')
        data = {
            'title': "Growpy FS Web Data Visualizer",
            'year': str(datetime.now().strftime('%Y'))
        }
        context = RequestContext(request, data)
        return HttpResponse(template.render(context))


class ChartFileSystemStatsJSON(View):
    """
    /getstat/1/1/2013/09/12/
    """
    def get(self, request, node, fs, year, fmonth='01', tmonth='12', sday='01', eday='31'):
        try:
            if tmonth < fmonth:
                fmonth, tmonth = tmonth, fmonth
            filesystems = Filesystem.objects.filter(node_id=node, fs_id=fs)
            data = {
                "stats": list(),
                "total": list()
            }
            for fs in filesystems:
                if fmonth != tmonth:
                    from calendar import monthrange
                    last_day = str(monthrange(int(year), int(tmonth))[1])
                    date_range = [year + '-' + fmonth + '-01', year + '-' + tmonth + '-' + last_day]
                    stats = Status.objects.filter(fs_id=fs.fs_id, status_date__range=date_range, status_date__day='01')
                else:
                    date_range = [year + '-' + fmonth + '-' + sday, year + '-' + tmonth + '-' + eday]
                    stats = Status.objects.filter(fs_id=fs.fs_id, status_date__range=date_range)
                i = 0
                for stat in stats:
                    data['stats'].append({
                        'date': str(stat.status_date.strftime('%Y-%m-%d')),
                        'name': fs.fs_name + ' mounted on ' + fs.fs_pmount,
                        'size': round(stat.status_size / 1024 / 1024, 2),
                        'used': round(stat.status_used / 1024 / 1024, 2),
                        'free': round((stat.status_size - stat.status_used) / 1024 / 1024, 2)
                    })
                    if i == 0:
                        max_used = stat.status_used
                        min_used = stat.status_used
                    if min_used > stat.status_used:
                        min_used = stat.status_used
                    if max_used < stat.status_used:
                        max_used = stat.status_used
                    i += 1
            if i > 0:
                data['total'].append({
                    'max': round(max_used / 1024 / 1024, 2),
                    'min': round(min_used / 1024 / 1024, 2),
                    'recommended': round((max_used - min_used) / 1024 / 1024, 2)
                })
        except ObjectDoesNotExist:
            data = {"result": "not found"}

        return HttpResponse(json.dumps(data), content_type='application/json')


class GetFSByNodeJSON(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, id):
        data = {"Message": None,
                "Result": "OK",
                "Records": list(),
                "TotalRecordCount": None}
        filesystems = Filesystem.objects.filter(node_id=id)
        for fs in filesystems:
            data['Records'].append({
                'fs_id': fs.fs_id,
                'fs_name': fs.fs_name,
                'fs_pmount': fs.fs_pmount
            })
        return HttpResponse(json.dumps(data), content_type='application/json')


class GetNodesJSON(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        data = {"Message": None,
                "Result": "OK",
                "Records": list(),
                "TotalRecordCount": None}
        try:
            start = int(request.GET['jtStartIndex'])
            end = start + int(request.GET['jtPageSize'])
            item_sort = request.GET['jtSorting'].split()[0]
            if request.GET['jtSorting'].split()[1] == 'DESC':
                item_sort = '-' + item_sort
            data['TotalRecordCount'] = Node.objects.count()
            for node in Node.objects.all().order_by(item_sort)[start:end]:
                data["Records"].append({
                    'node_id': node.node_id,
                    'node_name': node.node_name,
                    'node_os_name': node.node_os_name,
                    'node_login': node.node_login
                })
        except ObjectDoesNotExist:
            data = {"Message": "Error: Node records not found.",
                    "Result": "ERROR"}
        return HttpResponse(json.dumps(data), content_type='application/json')


class NodeList(TemplateView):

    def dispatch(self, request):
        template = loader.get_template('nodes.html')
        data = {'title': "Nodes",
                'os_options': OS_CHOICES
                }
        context = RequestContext(request, data)
        return HttpResponse(template.render(context))


class RangeSelector(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        template = loader.get_template('range_selector.html')
        fs = Filesystem.objects.filter(node_id=request.POST["node_id"], fs_id=request.POST["fs_id"])[0]
        firstat = Status.objects.filter(fs_id=fs.fs_id).order_by('status_date')[0]
        data = {
            "node_id": request.POST["node_id"],
            "fs_id": request.POST["fs_id"],
            "start_year": firstat.status_date.strftime("%Y")
        }
        context = RequestContext(request, data)
        return HttpResponse(template.render(context))


class Graph(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        template = loader.get_template('graph.html')
        data = {
            "node_id": request.POST["node_id"],
            "fs_id": request.POST["fs_id"],
            "year": request.POST["year"],
            "sm": request.POST["start_month"],
            "em": request.POST["end_month"],
            #"sd": request.POST["start_day"],
            #"ed": request.POST["end_day"],
        }
        context = RequestContext(request, data)
        return HttpResponse(template.render(context))


class NodeAdd(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request,):
        if request.method == "POST":
            n = Node.objects.filter(node_name=request.POST['node_name'])
            if n:
                data = {"Message": "Error: Node name exists.",
                        "Result": "ERROR"}
            elif (request.POST['node_name'] != '' and request.POST['node_os_name'] != '' and
                    request.POST['node_login'] != '' and request.POST['node_password'] != ''):
                cipher = AESCipher(settings.AES_KEY)
                passwd = cipher.encrypt(request.POST['node_password'])
                n = Node(node_name=request.POST['node_name'],
                         node_os_name=request.POST['node_os_name'],
                         node_login=request.POST['node_login'],
                         node_password=passwd)
                try:
                    n.save()
                    data = {"Result": "OK",
                            "Record": {
                                "node_id": n.node_id,
                                "node_name": n.node_name,
                                "node_os_name": n.node_os_name,
                                "node_login": n.node_login,
                                "node_password": n.node_password
                            },
                            "Message": request.POST['node_name'] + " Saved OK"}
                except IntegrityError as e:
                    data = {"Message": "Error: {0}".format(e),
                            "Result": "ERROR"}
            else:
                data = {"Result": "ERROR",
                        "Message": "Error: Invalid form"}
        else:
            data = {"Message": "Error: POST method is required.",
                    "Result": "ERROR"}
        return HttpResponse(json.dumps(data), content_type='application/json')


class NodeDel(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        if request.method == "POST":
            n = Node.objects.get(node_id=request.POST['node_id'])
            if not n:
                data = {"Result": "ERROR",
                        "Message": "Error: Object Does Not Exist"}
            else:
                n.delete()
                data = {"Result": "OK"}
        else:
            data = {"Message": "Error: POST method is required.",
                    "Result": "ERROR"}
        return HttpResponse(json.dumps(data), content_type='application/json')


class NodeUpdate(TemplateView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request,):
        if request.method == "POST":
            if (request.POST['node_id'] != '' and request.POST['node_name'] != '' and
                    request.POST['node_os_name'] != '' and request.POST['node_login'] != ''):

                n = Node.objects.get(node_id=request.POST['node_id'])
                if not n:
                    data = {"Message": "Error: Object Does not exist",
                            "Result": "ERROR"}
                else:
                    n.node_name = request.POST['node_name']
                    n.node_os_name = request.POST['node_os_name']
                    n.node_login = request.POST['node_login']
                    if request.POST['node_password'] != '':
                        cipher = AESCipher(settings.AES_KEY)
                        n.node_password = cipher.encrypt(request.POST['node_password'])
                    try:
                        n.save()
                        data = {"Result": "OK",
                                "Record": {
                                    "node_id": n.node_id,
                                    "node_name": n.node_name,
                                    "node_os_name": n.node_os_name,
                                    "node_login": n.node_login,
                                    "node_password": cipher.decrypt(n.node_password).decode('utf-8')
                                },
                                "Message": request.POST['node_name'] + " Saved OK"}
                    except IntegrityError as e:
                        data = {"Message": "Error: {0}".format(e),
                                "Result": "ERROR"}
            else:
                data = {"Result": "ERROR",
                        "Message": "Error: Invalid form"}
        else:
            data = {"Message": "Error: POST method is required.",
                    "Result": "ERROR"}
        return HttpResponse(json.dumps(data), content_type='application/json')
