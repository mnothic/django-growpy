from __future__ import unicode_literals
from django.db import models

OS_CHOICES = (
    ('AIX', 'AIX'),
    ('DragonFly', 'DragonFlyBSD'),
    ('FreeBSD', 'FreeBSD'),
    ('GNU/kFreeBSD', 'GNU/kFreeBSD'),
    ('HP-UX', 'HP-UX'),
    ('GNU', 'Hurd'),
    ('IRIX64', 'Irix'),
    ('Linux', 'Linux'),
    ('Darwin', 'Max OS X'),
    ('Minix', 'Minix'),
    ('NetBSD', 'NetBSD'),
    ('OpenBSD', 'OpenBSD'),
    ('QNX', 'QNX'),
    ('SunOS', 'Solaris'),
    ('UnixWare', 'UnixWare')
)


class Node(models.Model):

    node_id = models.IntegerField(primary_key=True, unique=True, null=False)
    node_name = models.CharField(max_length=128, unique=True)
    node_os_name = models.CharField(max_length=24, unique=False, choices=OS_CHOICES)
    node_login = models.CharField(max_length=24, unique=False)
    node_password = models.CharField(max_length=128, unique=False)

    class Meta:
        db_table = 'node'


class Filesystem(models.Model):
    fs_id = models.PositiveIntegerField(primary_key=True, unique=True, null=False)
    node = models.ForeignKey(Node)
    fs_name = models.CharField(max_length=128, unique=False)
    fs_pmount = models.CharField(max_length=256, unique=False)

    class Meta:
        db_table = 'filesystem'


class Status(models.Model):
    status_id = models.IntegerField(primary_key=True, unique=True, null=False)
    fs = models.ForeignKey(Filesystem)
    status_size = models.IntegerField()
    status_used = models.IntegerField()
    status_date = models.DateTimeField()

    class Meta:
        db_table = 'status'
