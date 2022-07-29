var user_id, token;


$(document).ready(function () {
    user_id = $("#content #user_id").html();
    token = $("#content #page_user_token").html();
    // csrf = $("#content #csrf").children("input").attr("value");


    $(".like-button").on("click", function (e) { 
        e.preventDefault();

        let btn = $(e.currentTarget);
        let post_id = btn.parent().parent().parent().attr("post_id");
        let like_p = btn.parent().children("span");
        let method = btn.hasClass("active") ? 'remove': 'add';

        $.ajax({
            type: "POST",
            url: `/news/api/like?token=${token}&post_id=${post_id}&method=${method}`,
            data: {
                "token": token,
                "post_id": post_id,
                "method": method
            },
            success: function (response) {
                like_p.html(response['likes']);
                if (method === 'remove') {
                    btn.html('<img src="/static/news/img/like.png" alt="" width="32" height="32">');
                    btn.removeClass("active");
                } else {
                    btn.html('<img src="/static/news/img/like_active.png" alt="" width="32" height="32">');
                    btn.addClass("active");
                }
            }
        }).fail(function () { 
            alert('Что-то пошло не так. Перезагрузите страницу.');
         });
    });
});


function fetch_news(sender) {
    let post_id = $(".main-line .card").last().attr("post_id");
    $.ajax({
        type: "GET",
        url: `/news/ajax/?user_id=${user_id}&post_id=${post_id}`,
        success: function (response) {
            let data = response["data"];
            let insert_html = "";
            if (data.length != 0) {
                data.forEach(element => {
                    insert_html = insert_html + 
                    `
                    <div class="card" post_id="${element['id']}">
                        <div class="card-header">
                        <div class="user-info">
                            user
                        </div>
                        <div class="right-pannel">
                            actions
                        </div>
                        </div>
                        <div class="card-body">
                        <h5 class="card-title">${element['title']}</h5>
                        <p class="card-text">${element['content']}</p>
                        <a href="#" class="btn btn-primary">Go somewhere</a>
                        </div>
                        <div class="card-footer">
                            test
                        </div>
                    </div>
                    <br>
                    `;
                });
                let more = $(".main-line .more");
                $(".main-line .more").remove();
                $(".main-line").html($(".main-line").html() + insert_html);
                more.appendTo($(".main-line"));
            } else {
                console.log('None');
            }
        },
    });
}