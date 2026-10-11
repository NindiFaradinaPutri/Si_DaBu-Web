(function ($) {

	'use strict';

	var datatableInit = function () {
		var $table = $('#datatable-kegiatan');

		// format function for row details
		var fnFormatDetails = function (datatable, tr) {
			var data = datatable.fnGetData(tr);
			var title = data[3];
			var div = $('<div/>').addClass('loading').text('Loading...');

			if (title !== null || title !== '') {
				$.ajax({
					type: "POST",
					url: '/ajax/add_kegiatan_detail/',
					datatype: 'json',
					data: { 'title': title },
					success: function (data) {
						div.html(data).removeClass('loading');
					}
				});
			};
			
			return div;


		};

		// insert the expand/collapse column
		var th = document.createElement('th');
		var td = document.createElement('td');
		td.innerHTML = '<i data-toggle class="far fa-plus-square text-primary h5 m-0" style="cursor: pointer;"></i>';
		td.className = "text-center";

		$table
			.find('thead tr').each(function () {
				this.insertBefore(th, this.childNodes[0]);
			});

		$table
			.find('tbody tr').each(function () {
				this.insertBefore(td.cloneNode(true), this.childNodes[0]);
			});

		// initialize
		var datatable = $table.dataTable({
			dom: '<"row"<"col-lg-6"l><"col-lg-6"f>><"table-responsive"t>p',
			aoColumnDefs: [{
				bSortable: false,
				aTargets: [0]
			}],
			aaSorting: [
				[1, 'asc']
			]
		});

		// add a listener
		$table.on('click', 'i[data-toggle]', function () {
			var $this = $(this),
				tr = $(this).closest('tr').get(0);

			if (datatable.fnIsOpen(tr)) {
				$this.removeClass('fa-minus-square').addClass('fa-plus-square');
				datatable.fnClose(tr);
			} else {
				$this.removeClass('fa-plus-square').addClass('fa-minus-square');
				datatable.fnOpen(tr, fnFormatDetails(datatable, tr), 'details');
			}
		});
	};

	$(function () {
		datatableInit();
	});

}).apply(this, [jQuery]);