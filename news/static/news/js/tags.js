let show = true;
const MAX_ITEMS = 10;

$(document).ready(function () {
    let items = $("#id_categories div");
    if (items.length > MAX_ITEMS - 1) {
        set_hidden(true);
        let parrent = $("#id_categories");
        parrent.html(parrent.html() + '<button type="button" id="size_formatter" class="size_formatter" onclick=show_f()>Развернуть</button>');
    }

    
});

function set_hidden(value) { 
    $.each($("#id_categories div"), function (index, element) { 
        if (index > MAX_ITEMS - 1) {
            element.hidden = value;
        }
    });
}

function show_f() {  
    let sender = $("#size_formatter");
    if (show) {
        sender.text("Свернуть");
        sender.addClass('clicked');

    } else {
        sender.text("Развернуть");
        sender.removeClass('clicked');
    }
    show = !show;
    set_hidden(show);
}