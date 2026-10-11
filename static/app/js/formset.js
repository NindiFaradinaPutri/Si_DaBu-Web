var form_count = Number($("[name=form-TOTAL_FORMS]").val());
var min_form_count = Number($("[name=form-MIN_NUM_FORMS]").val());
var max_form_count = Number($("[name=form-MAX_NUM_FORMS]").val());
var url = $('#id_url_formset').val();

$("#add-form").click(function () {
    if (form_count < max_form_count) {
        form_count++;
        $.ajax({
            type: "POST",
            url: url,
            datatype: 'json',
            data: { 'form_count': form_count },
            success: function (data) {
                $('#formset_area').append(data);

                if (form_count >= 2) {
                    $("#remove-form").removeClass('d-none');
                }

                $("[name=form-TOTAL_FORMS]").val(form_count);
            }
        });
    } else {
        new PNotify({
            title: 'Attention!',
            text: 'The number of form additions has exceeded the limit',
            type: 'custom',
            addclass: 'notification-danger',
            icon: 'fas fa-check'
        });
    }
});

$("#remove-form").click(function () {
    $("#id_formappend_" + (form_count - 1)).remove();
    form_count--;

    if (form_count < 2) {
        $("#remove-form").addClass('d-none');
    }

    $("[name=form-TOTAL_FORMS]").val(form_count);
});