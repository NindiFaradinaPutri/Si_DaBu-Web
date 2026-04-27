/*Event ketika click view pengguna*/
$("#change_response").click(function (event) {
    event.preventDefault();
    var form = $('#response_form');

    $.ajax({
        type: "POST",
        url: '/ajax/complaint_response_update/',
        datatype: 'json',
        data: form.serialize(),
        success: function (data) {
            if (data.html) {
                $("#response_area").html('');
                $("#response_area").append(data.html);
                $("#response_area").focus();

                $("#response_status").html(data.status);
                $("#response_date").html(data.date);

                new PNotify({
                    title: 'Complaint Data',
                    text: data.message,
                    type: 'custom',
                    delay: 2500,
                    addclass: 'notification-success',
                    icon: 'fas fa-check'
                });
            } else {
                new PNotify({
                    title: 'Complaint Data',
                    text: data.message,
                    type: 'custom',
                    delay: 2500,
                    addclass: 'notification-danger',
                    icon: 'fas fa-times-circle'
                });
            }


        }
    });
});

