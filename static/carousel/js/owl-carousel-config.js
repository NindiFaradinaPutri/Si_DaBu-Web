$(document).ready(function () {
    $(".owl-carousel").owlCarousel({
        loop: true,
        nav: true,
        dots: false,
        margin: 10,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true,
        navText: ["<div class='bs-button'><i class='fal fa-chevron-left'></i></div>", "<div class='bs-button'><i class='fal fa-chevron-right'></i></div>"],
        responsive: {
            0: {
                items: 1,
                nav: false,
            },
            600: {
                items: 3,
                nav: true,
            },
            1000: {
                items: 1,
                nav: true,
            }
        }
    });
});