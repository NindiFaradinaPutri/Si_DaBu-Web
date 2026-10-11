$(document).ready(function () {
    $('.datepicker').datepicker({
        format: 'dd-mm-yyyy',
    });
    $('.monthpicker').datepicker({
        format: "mm-yyyy",
        viewMode: "months",
        minViewMode: "months"
    });
});

$('#select_date').click(function (e) {
    var start_date = $('#id_start_date').val();
    var end_date = $('#id_end_date').val();

    $.ajax({
        type: "POST",
        url: '/ajax/filter_gl_by_date/',
        datatype: 'json',
        data: { 'start_date': start_date, 'end_date': end_date },
        success: function (data) {
            $('#table_area').empty();
            $('#table_area').append(data);
        }
    });    
});

$('#select_month').click(function (e) {
    var month = $('#id_select_month').val();

    $.ajax({
        type: "POST",
        url: '/ajax/filter_gl_by_month/',
        datatype: 'json',
        data: { 'month': month },
        success: function (data) {
            $('#table_area').empty();
            $('#table_area').append(data);
        }
    });
});