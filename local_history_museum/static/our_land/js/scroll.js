$(window).scroll(function () {
    let scroll = $('.scrollup');
    let artTop = $("#article").offset().top;

    if ($(this).scrollTop() > artTop) {
        scroll.fadeIn();
    } else {
        scroll.fadeOut();
    }
});

$('.scrollup').click(function () {
    $("html, body").animate({
        scrollTop: 0
    }, 600);
    return false;
});