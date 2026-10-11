$(document).ready(function () {
    $('.datepicker').datepicker({
        format: 'dd-mm-yyyy',
    });
    $('.monthpicker').datepicker({
        format: "mm-yyyy",
        viewMode: "months",
        minViewMode: "months"
	});

	dataTableInit();
});

function print_khotbah(){
	var start_date = $('#start_date').data('date');
	var end_date = $('#end_date').data('date');
	var pass_code = $('#id_pass_code').val();

	window.open('/print/khotbah/jumat/' + start_date + '/' + end_date + '/' + pass_code);
}

function print_keuangan() {
	var start_date = $('#start_date').data('date');
	var end_date = $('#end_date').data('date');
	var pass_code = $('#id_pass_code_keuangan').val();

	window.open('/print/keuangan/' + start_date + '/' + end_date + '/' + pass_code);
}

function copy_rekening() {
	var rekening_text = $("#copas").data('rek').replace(/\D/g,'');

	navigator.clipboard.writeText(rekening_text);
	alert("No Rekening sudah dicopy: " + rekening_text);
};

$("#id_confirm_modal").click(function (e) {
	e.preventDefault();
	print_khotbah();	
});

$("#id_keuangan_modal").click(function (e) {
	e.preventDefault();
	print_keuangan();
});

function dataTableInit() {
	
	var $table = $('#datatable-rekening');

	var table = $table.dataTable({
		sDom: '<"text-right mb-md"T><"row"<"col-lg-6"l><"col-lg-6"f>><"table-responsive"t>p',
		buttons: [
			{
				extend: 'print',
				text: 'Print'
			},
			{
				extend: 'excel',
				text: 'Excel'
			},
			{
				extend: 'pdf',
				text: 'PDF',
				customize: function (doc) {
					var colCount = new Array();
					$('#datatable-rekening').find('tbody tr:first-child td').each(function () {
						if ($(this).attr('colspan')) {
							for (var i = 1; i <= $(this).attr('colspan'); $i++) {
								colCount.push('*');
							}
						} else { colCount.push('*'); }
					});
					doc.content[1].table.widths = colCount;
				}
			}
		]
	});

	$('<div />').addClass('dt-buttons mb-2 pb-1 text-right').prependTo('#datatable-rekening_wrapper');

	$table.DataTable().buttons().container().prependTo('#datatable-rekening_wrapper .dt-buttons');

	$('#datatable-rekening_wrapper').find('.btn-secondary').removeClass('btn-secondary').addClass('btn-default');
	
};
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
			$('#table_area').append(data.html);

			dataTableInit();

            $('#start_date').val(data.start_date);
			$('#end_date').val(data.end_date);
			$('#start_date').data('date', data.start_date_format);
			$('#end_date').data('date', data.end_date_format);
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
			$('#table_area').append(data.html);

			dataTableInit();

            $('#start_date').val(data.start_date);
			$('#end_date').val(data.end_date);
			$('#start_date').data('date', data.start_date_format);
			$('#end_date').data('date', data.end_date_format);
        }
    });
});