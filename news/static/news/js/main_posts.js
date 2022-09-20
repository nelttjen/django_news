var user_id, token, csrf;

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

$(document).ready(() => {
    user_id = $("#content #user_id").html();
    token = getCookie("user_token");
    csrf = getCookie("csrftoken");
    // csrf = $("#content #csrf").children("input").attr("value");

    fetch_avatars();
    fetch_time();
    connect_buttons();
});

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


function fetch_news(sender) {
    let post_id = $(".main-line .card").last().attr("post_id");
    $.ajax({
        type: "POST",
        url: `/news/api/news`,
        data: {

            'user_token': token,
            'post_id': post_id,
        },
        headers: {
            'X-CSRFToken': csrf,
        },
        success: function (response) {
            let data = response["data"];
            let insert_html = "";
            if (data.length != 0) {
                data.forEach(element => {
                    let footer;
                    if (element['has_login']) {
                        let div_like;
                        if (element['post_liked']) {
                            div_like = `
                            <div class="like-button active" id="like-button">
                                <img src="/static/news/img/like_active.png" alt="" width="32" height="32">
                            </div>
                            `;
                        } else {
                            div_like = `
                            <div class="like-button" id="like-button">
                                <img src="/static/news/img/like.png" alt="" width="32" height="32">
                            </div>
                            `;
                        }

                        footer = 
                        `
                        <div class="likes">
                            ${div_like}
                            <span style="margin-left: 10px;">${element['post_likes']}</span>
                        </div>
                        <div class="comments">
                            <a class="comm-button" href="/news/posts/id${element['id']}#comment">
                                <img src="/static/news/img/comment.png" alt="com">
                            </a>
                            <span class="comm-count">${element['post_comms']}</span>
                        </div>
                        <div class="reposts">
                            reps
                        </div>
                        `;
                    } else {
                        footer = '<span><a href="/auth/login">Авторизуйтесь</a> для дополнительный действий</span>'
                    }

                    insert_html = insert_html + 
                    `
                    <div class="card" post_id="${element['id']}">
                    <div class="card-header">
                      <div class="user-info">
                        <a href="/news/users/id${element['author_id']}"><img src="/static/user_profile/img/profile_images/${element['author_id']}.png" class="card-avatar avatar-validation"></a>
                        <div style="margin-left: 10px;">
                            <a href="/news/users/id${element['author_id']}"><p>${element['author_username']}</p></a>
                            <p>Отпубликовано: <span class="card-publish-time">${element['creation_date']}</span></p>
                        </div>
                    </div>
                      <div class="right-pannel">
                        actions
                      </div>
                    </div>
                    <div class="card-body">
                      <h5 class="card-title">${element['title']}</h5>
                      <p class="card-text">${element['content']}</p>
                      <a href="/news/posts/id${element['id']}" class="btn btn-primary">Посмотреть новость</a>
                    </div>
                    <div class="card-footer">
                        ${footer}
                    </div>
                </div>
                <br>
                    `;
                });
                let more = $(".main-line .more");
                $(".main-line .more").remove();
                $(".main-line").html($(".main-line").html() + insert_html);
                more.appendTo($(".main-line"));
                fetch_avatars();
                fetch_time();
                connect_buttons();
            } else {
                console.log('None');
            }
        },
    });
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

function connect_buttons() { 
    $('.like-button').click(function (e) { 
        e.preventDefault();
        like_ajax(e.currentTarget);
    });
    $('.more > button').click(function (e) { 
        e.preventDefault();
        fetch_news(e.currentTarget);
    });
 }