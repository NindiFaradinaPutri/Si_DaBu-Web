/* Pendukung AJAX POST */
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.href,
        sURLVariables = sPageURL.split('/'),
        sParameterName,
        i;


    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split(':');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? 0 : decodeURIComponent(sParameterName[1]);
        }
    }
    return 0;
};