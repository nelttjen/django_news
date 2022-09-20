$(document).ready(function () {
    fetch_avatars();

    token = getCookie("user_token");
    csrf = getCookie("csrftoken");

    $('.like-button').click(function (e) { 
        e.preventDefault();
        like_ajax(e.currentTarget);
    });
    
    fetch_time();
});

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function fetch_avatars() {
    let default_link = "/static/user_profile/img/default.png";
    let avatars = $(".avatar-validation");
    avatars.each((i, val) => {
         $.ajax({
            url: $(val).attr("src"),
         }).fail(
            () => {
                $(val).attr("src", default_link);
            }
         );
    });
}

function like_ajax(e) { 

    let btn = $(e);
    let post_id = btn.parent().parent().parent().attr("post_id");
    let like_p = btn.parent().children("span");
    let method = btn.hasClass("active") ? 'remove': 'add';

    $.ajax({
        type: "POST",
        url: `/api/v1/likes/${post_id}`,
        data: {
            "token": token,
            "method": method
        },
        headers: {
            'X-CSRFToken': csrf,
        },
        success: function (response) {
            if (response['message'] === 'OK') {
                like_p.html(response['likes']);
                if (method === 'remove') {
                    btn.html('<img src="/static/news/img/like.png" alt="" width="32" height="32">');
                    btn.removeClass("active");
                } else {
                    btn.html('<img src="/static/news/img/like_active.png" alt="" width="32" height="32">');
                    btn.addClass("active");
                }
            } 
            else alert('Что-то пошло не так. Перезагрузите страницу.');
        }
    })
}

function fetch_time() {
    let items = $(".card-publish-time");
    $.each(items, function (i, val) { 
        if (!$(val).hasClass('time-fetched')) {
            let item = $(val);
            let dateArray = item.html().split(":");
            let date = new Date(Date.UTC(dateArray[2], dateArray[1], dateArray[0], dateArray[3], dateArray[4], dateArray[5]));
            item.html(date.toLocaleString());
            $(val).addClass('time-fetched')
        }
    });
}