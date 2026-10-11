var CURRENT_PAGE = location.pathname,
    $MAIN_NAV = $("#mainNav");

function del_active_move() {
    $MAIN_NAV.find("li a").removeClass("active current-page-active");
    /*$MAIN_NAV.find("li ul").slideUp();*/    /*comment agar sub menu muncul*/
}

function show_password() {
    var x = document.getElementById("id_password");
    var icon = document.getElementById("icon_pass");
    icon.classList.toggle("fa-eye-slash");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
};

function show_password2() {
    var x = document.getElementById("id_confirm_password");
    var icon = document.getElementById("icon_confirm_pass");
    icon.classList.toggle("fa-eye-slash");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
};

//$(function () {
//    del_active_move();
//    $('.nav-link').each(function () {
//        var $this = $(this);
//        if (CURRENT_PAGE == '/') {
//            CURRENT_PAGE = '/home/';
//        }
//        // if the current path is like this link, make it active
//        if ($this.attr('href').indexOf(CURRENT_PAGE) !== -1) {
//            $this.addClass('active current-page-active');
//        }
//    })
//});

function validateEmail(email) {
    const re = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
    return re.test(email);
};





