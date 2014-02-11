// base js growpy
function getCookie(cname)
{
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++)
      {
      var c = ca[i].trim();
      if (c.indexOf(name)==0) return c.substring(name.length,c.length);
      }
    return "";
}

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
}

function daysInMonth(iMonth, iYear)
{
    return 32 - new Date(iYear, iMonth, 32).getDate();
}

function range_button()
{
    var button = " " +
    '<tr id="button">' +
        '<td></td>' +
        '<td>' +
            '<div class="ui-dialog-buttonset">' +
                '<button type="button" id="draw_button" class="ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only ui-state-focus" role="button" aria-disabled="false">' +
                    '<span class="ui-button-text">Draw</span>' +
                '</button>' +
            '</div>' +
        '</td>' +
    '</tr>'
    return button
}

function by_year(startYear) {
    var currentYear = new Date().getFullYear();
    var select = '<select id="by_year">' +
            '<option>Select</option>';
    while ( currentYear >= startYear) {
        select += "<option>" + (currentYear--) + "</option>"
    }
    select += "</select>"
    $("#range-table").append('<tr id="by_year">' +
            "<td>Year</td>" +
            "<td>" + select +
            "</td>" +
            "</tr>"
    );
}

function range_month(type){
    var monthNames = [ "January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December" ];
    var select = '<select id="by_month_' + type +'">' +
            '<option>Select</option>';
    for ( var month in monthNames ) {
        var i = month;
        ++i;
        select += '<option value="' + i + '">' + monthNames[month] + '</option>';
    }
    select += '</select>';

    $("#range-table").append('<tr id="month_'+type+'">' +
            "<td>" + toTitleCase(type) + " month</td>" +
            "<td>" + select +
            "</td>" +
            "</tr>"
    );
}

function by_month_year(type) {
    by_year(type);
    $("tr#by_year").attr("id", "by_month_year");
    $("select#by_year").attr("id", "by_month_year");
}

function by_day_year(type) {
    by_year(type);
    $("#by_year").attr("id", "by_day_year");
}
//draw button code
$(document).on("click", "#draw_button", function (){
    $("div.overlay > div.chart").empty();
    $("div.overlay > div.chart").load('/node/fs/chart/', {
        'node_id': getCookie("node"),
        'fs_id': getCookie("fs"),
        'year': getCookie("year"),
        'start_month': getCookie("start_month"),
        'end_month': getCookie("end_month")
    }).fadeIn('slow');
});

$(document).ready(function () {
    $('#container').load("/node/list/");
});

$(function() {
    $( ".chart" ).draggable();
});


// selected year entire range
$(document).on('change',"select#by_year", function(){
    $("select#by_year > option:selected").each(function(){
        $("tr#button").remove();
        $("#range-table").append(range_button());
        document.cookie = "year=" + $(this).text();
        document.cookie = "start_month=01"
        document.cookie = "end_month=12"
        //console.log($(this).text());
    });
});
// end year entire range

// select month range
$(document).on('change',"select#by_month_year", function(){
    $("select#by_month_year > option:selected").each(function(){
        $("tr#month_start").remove();
        $("tr#month_end").remove();
        $("tr#button").remove();
        $("#range-table").append(range_month('start'));
        document.cookie = "year=" + $(this).text();
    });
});

$(document).on('change',"select#by_month_start", function(){
    $("#by_month_start > option:selected").each(function(){
        $("tr#month_end").remove();
        $("tr#button").remove();
        $("#range-table").append(range_month('end'));
        if ($(this).val().length == 1)
            document.cookie = "start_month=0" + $(this).val();
        else
            document.cookie = "start_month=" + $(this).val();;
    });
});

 $(document).on('change',"select#by_month_end", function(){
    $("select#by_month_end > option:selected").each(function(){
        $("tr#button").remove();
        $("#range-table").append(range_button());
        if ($(this).val().length == 1)
            document.cookie = "end_month=0" + $(this).val();
        else
            document.cookie = "end_month=" + $(this).val();
    });
});
// end month range selector

// days range selector


// end days range selector