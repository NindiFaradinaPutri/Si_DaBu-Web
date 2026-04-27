$('#deleteConfirmationModals').on('show.bs.modal', function (e) {
    $("#del_item").html($(e.relatedTarget).data('name'));
    $(this).find('.modal-confirm').attr('href', $(e.relatedTarget).data('href'));
});