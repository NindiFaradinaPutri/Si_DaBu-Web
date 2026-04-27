
$('#id_submit').click(function (e) {
    e.preventDefault();
    var username = $('#id_username').val();

    $.ajax({
		type: "POST",
        url: '/ajax/check_account_activation/',
        data:{'username':username},
        datatype: 'json',
        success: function (data) {
            if(data.is_active == true){
                $('#frmLogin').submit();
            }else if(data.is_active == false){
                $("#account_item").html(username);
                $('#uniqueCodeModals').modal('show');
            }else{
                $('#frmLogin').submit();
            }
        }
    });
});

$('#btn_activate').click(function (e) {
    $('#uniqueCodeModals').modal('hide');
    $('#id_unique_code').val($('#id_token_code').val());
    $('#frmSignIn').submit();
});