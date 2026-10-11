function refresh_page() {
    var form = $('#filter_form');
    var per_page = $('#id_per_page').val();
    var page = $('#p_page').val();
    var url = $('#id_url_filter').val();

    $.ajax({
        type: "POST",
        url: url,
        datatype: 'json',
        data: form.serialize() + "&per_page=" + per_page + "&page=" + page,
        success: function (data) {
            if ($("#tmp_table").length > 0) {
                $("#tmp_table").html('');
                $("#tmp_table").append(data);
                $("#tmp_table").focus();
            } else {
                $("#list_area").html('');
                $("#list_area").append(data);
                $("#list_area").focus();
            }
        }
    });
}

//Do Searching
$('#id_search').click(function (e) {
    e.preventDefault();
    $('#id_search').blur();
    refresh_page();
});

//Do Reset
$('#id_reset').click(function (e) {
    e.preventDefault();
    $(':input', '#filter_form').not(':button, :submit, :reset, :hidden').removeAttr('checked').removeAttr('selected').not(':checkbox, :radio, select').val('');
    $("#filter_form select").val("-1");

    $('#id_reset').blur();
    refresh_page();
});

//Change Jumlah Per Baris
$('#id_per_page').change(function (e) {
    e.preventDefault();
    $('#p_page').val('');
    refresh_page();

});

//Click Sort By
$("#tmp_table").on("click", "table tr th a[href]", function (e) {
    e.preventDefault();

    $('#p_page').val('');
    var urlParams = new RegExp('[\?&]sort=([^&#]*)').exec($(this).attr("href"));
    var sort_by = '';

    if (urlParams != null || urlParams.length <= 0) {
        sort_by = urlParams[1];
        $('#p_sort_by').val(sort_by);
    }

    refresh_page();
});

//Click Page in Pagination
$("#tmp_table").on("click", ".page-link", function (event) {
    var page = this.dataset.page;
    $('#p_page').val(page);

    refresh_page();
});

//Click Sort By
$("#list_area").on("click", "table tr th a[href]", function (e) {
    e.preventDefault();

    $('#p_page').val('');
    var urlParams = new RegExp('[\?&]sort=([^&#]*)').exec($(this).attr("href"));
    var sort_by = '';

    if (urlParams != null || urlParams.length <= 0) {
        sort_by = urlParams[1];
        $('#p_sort_by').val(sort_by);
    }

    refresh_page();
});

//Click Page in Pagination
$("#list_area").on("click", ".page-link", function (e) {
    e.preventDefault();
    var page = this.dataset.page;
    $('#p_page').val(page);

    refresh_page();
});