function fetch_news(sender) {
    sender.preventDefault()
    let user_id = $("#content #user_id").html();
    let post_id = $(".main-line .card").last().attr("post_id");
    $.ajax({
        type: "GET",
        url: `/news/ajax/?user_id=${user_id}&post_id=${post_id}`,
        success: function (response) {
            let data = response["data"];
            let insert_html = "";
            if (data.length != 0) {
                console.log(data);
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
