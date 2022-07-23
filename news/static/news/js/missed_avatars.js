$(document).ready(function () {
    let default_link = "/static/user_profile/img/default.png";
    let avatars = $(".avatar-validation");
    avatars.each(function (i, val) { 
         $.ajax({
            url: $(val).attr("src"),
         }).fail(
            function () {
                $(val).attr("src", default_link);
            }
         );
    });
});