"use strict";
$(document).ready(function () {
    let items = $(".card-publish-time");
    $.each(items, function (i, val) { 
         let item = $(val);
         let dateArray = item.html().split(":");
         let date = new Date(Date.UTC(dateArray[2], dateArray[1], dateArray[0], dateArray[3], dateArray[4], dateArray[5]));
         item.html(date.toLocaleString());
    });
});