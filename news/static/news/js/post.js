let show = true;
const MAX_ITEMS = 15;

$(document).ready(function () {
    let items = $("#id_categories div");
    if (items.length > MAX_ITEMS - 1) {
        set_hidden(true);
        let parrent = $("#id_categories");
        parrent.html(parrent.html() + '<button type="button" id="size_formatter" class="size_formatter" onclick=test_f()>Развернуть</button>');
    }

    
});

function set_hidden(value) { 
    $.each($("#id_categories div"), function (indexInArray, valueOfElement) { 
        if (indexInArray > MAX_ITEMS - 1) {
            valueOfElement.hidden = value;
        }
    });
}

function test_f() {  
    let sender = $("#size_formatter");
    if (show) {
        set_hidden(false);
        sender.text("Свернуть");
        sender.addClass('clicked');

    } else {
        set_hidden(true);
        sender.text("Развернуть");
        sender.removeClass('clicked');
    }
    show = !show;
}