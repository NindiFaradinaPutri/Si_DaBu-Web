var qurban_count = Number($("[name=qurban-TOTAL_FORMS]").val());
var min_qurban_count = Number($("[name=qurban-MIN_NUM_FORMS]").val());
var max_qurban_count = Number($("[name=qurban-MAX_NUM_FORMS]").val());

var $selected_row;
var $selected_id;

function tol_locale_number(value) {
    return value.toLocaleString('id');
}
//function reordering() {
    
//    $('#datatable-qurban').find('tr').each(function (index) {
//        order_no.last() += index;
//        $(this).find('td:eq(1)').html(order_no);    
//    });
    
//}

$("#add-qurban").click(function () {
    if (qurban_count < max_qurban_count) {
        qurban_count++;
        $.ajax({
            type: "POST",
            url: '/ajax/addform_qurban/',
            datatype: 'json',
            data: { 'qurban_count': qurban_count },
            success: function (data) {
                $('#append_form_area').append(data);
                $('[data-plugin-datepicker]').each(function () {
                    var $this = $(this),
                        opts = {};

                    var pluginOptions = $this.data('plugin-options');
                    if (pluginOptions)
                        opts = pluginOptions;

                    $this.themePluginDatePicker(opts);
                });

                $('.select2').select2({
                    theme: 'bootstrap',
                    width: '100%',
                });

                $('.number-mask').mask("#.##0", { reverse: true });


                if (qurban_count >= 2) {
                    $("#remove-qurban").removeClass('d-none');
                }

                $("[name=qurban-TOTAL_FORMS]").val(qurban_count);

                //reordering();
            }
        });
    } else {
        new PNotify({
            title: 'Perhatian!',
            text: 'Jumlah penambahan item qurban sudah melebih batas (maks 300)',
            type: 'custom',
            addclass: 'notification-danger',
            icon: 'fas fa-check'
        });
    }
});

$("#remove-qurban").click(function () {
    $("#id_qurbanappend_" + (qurban_count - 1)).remove();
    qurban_count--;

    if (qurban_count < 2) {
        $("#remove-qurban").addClass('d-none');
    }

    $("[name=qurban-TOTAL_FORMS]").val(qurban_count);
    //reordering();
});

$('#deleteConfirmationModals').on('show.bs.modal', function (e) {
    $selected_row = $(e.relatedTarget);
    
    $("#del_item").html($(e.relatedTarget).data('name'));
    $(this).find('.modal-confirm').attr('href', $(e.relatedTarget).data('href'));
});
$('.modal-confirm').click(function (e) {
    e.preventDefault();
    $parent = $selected_row.closest('tr');
    $selected_id = $parent.find('.d-none').find('[type=hidden]').val();

    if ($selected_row && $selected_id) {
        
        if ($parent) {
            $.ajax({
                type: "POST",
                url: '/ajax/delete_qurban/',
                datatype: 'json',
                data: { 'id': $selected_id },
                success: function (data) {
                    new PNotify({
                        title: 'Informasi!',
                        text: 'Data berhasil dihapus',
                        type: 'custom',
                        addclass: 'notification-info',
                        icon: 'fas fa-check'
                    });
                }
            });
            
        }

    } else {
        
        new PNotify({
            title: 'Informasi!',
            text: 'Data tidak berhasil dihapus',
            type: 'custom',
            addclass: 'notification-danger',
            icon: 'fas fa-check'
        });
    };

    $parent.remove();
    qurban_count--;

    if (qurban_count < 2) {
        $("#remove-qurban").addClass('d-none');
    }

    $("[name=qurban-TOTAL_FORMS]").val(qurban_count);
    $('#deleteConfirmationModals').modal('hide');
    //reordering();
    
});

$('#calculate-qurban').click(function (e) {
    recalculate();
});
