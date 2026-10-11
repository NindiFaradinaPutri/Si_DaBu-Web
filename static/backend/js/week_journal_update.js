var journal_count = Number($("[name=journal-TOTAL_FORMS]").val());
var min_journal_count = Number($("[name=journal-MIN_NUM_FORMS]").val());
var max_journal_count = Number($("[name=journal-MAX_NUM_FORMS]").val());
var $selected_row;
var $selected_id;

function tol_locale_number(value) {
    return value.toLocaleString('id');
}
function reordering() {
    var order_no = 0;
    
    $('#datatable-transaction').find('tr').each(function (index) {
        order_no = index++;
        $(this).find('td:eq(2)').html(order_no);    
    });
    
}

function recalculate() {
    var temp_total = parseInt(last_fix_balance.replace(/([-,.€~!@#$%^&*()_+=`{}\[\]\|\\:;'<>])+/g, ''));
    $('#datatable-transaction').find('tr').each(function (index) {
        if (index > 0) {
            var status = $(this).find('td:eq(6)').find('option:selected').text();
            var debet = parseInt($(this).find('td:eq(7)').find('.number-mask').val().replace(/([-,.€~!@#$%^&*()_+=`{}\[\]\|\\:;'<>])+/g, ''));
            var kredit = parseInt($(this).find('td:eq(8)').find('.number-mask').val().replace(/([-,.€~!@#$%^&*()_+=`{}\[\]\|\\:;'<>])+/g, ''));

            if (status === 'Saldo Akhir') {
                temp_total = kredit ? kredit : 0;
                $(this).find('td:eq(9)').find('.number-mask').val(tol_locale_number(kredit?kredit:0));
            } else {
                if (debet) {
                    temp_total -= debet;
                    $(this).find('td:eq(9)').find('.number-mask').val(tol_locale_number(temp_total));
                };

                if (kredit) {
                    temp_total += kredit;
                    $(this).find('td:eq(9)').find('.number-mask').val(tol_locale_number(temp_total));

                };
            };
        }
    });
}

$("#add-journal").click(function () {
    if (journal_count < max_journal_count) {
        journal_count++;
        $.ajax({
            type: "POST",
            url: '/ajax/addform_journal_week/',
            datatype: 'json',
            data: { 'journal_count': journal_count },
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


                if (journal_count >= 2) {
                    $("#remove-journal").removeClass('d-none');
                }

                $("[name=journal-TOTAL_FORMS]").val(journal_count);

                reordering();
            }
        });
    } else {
        new PNotify({
            title: 'Perhatian!',
            text: 'Jumlah penambahan item survey sudah melebih batas (maks 300)',
            type: 'custom',
            addclass: 'notification-danger',
            icon: 'fas fa-check'
        });
    }
});

$("#remove-journal").click(function () {
    $("#id_journalappend_" + (journal_count - 1)).remove();
    journal_count--;

    if (journal_count < 2) {
        $("#remove-journal").addClass('d-none');
    }

    $("[name=journal-TOTAL_FORMS]").val(journal_count);
    reordering();
});

$('#week_journal_update').submit(function () {
    $('.number-mask').unmask();
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
                url: '/ajax/delete_week_journal/',
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
    journal_count--;

    if (journal_count < 2) {
        $("#remove-journal").addClass('d-none');
    }

    $("[name=journal-TOTAL_FORMS]").val(journal_count);
    $('#deleteConfirmationModals').modal('hide');
    reordering();
    
});

$('#calculate-journal').click(function (e) {
    recalculate();
});
