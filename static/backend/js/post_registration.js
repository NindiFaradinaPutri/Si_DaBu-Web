$('#id_negara').change(function(e){
    var $this = $(this)
    var negara = $this.val();

    if (negara !== null || negara.length() > 0){
        $.ajax({
            type: "POST",
            url: '/ajax/akses_provinsi/',
            datatype: 'json',
            data: {'negara':negara},
            success: function (data) {
                if (data){
                    var provinsi = $('#id_provinsi');

                    provinsi.empty().trigger('change.select2');

                    var option = new Option('Pilih Provinsi', 0, true, true);
                    provinsi.append(option).trigger('change.select2');
                    

                    for(var i=0; i < data.length; i++){
                        option = new Option(data[i].fields.nama_provinsi, data[i].pk, false, true);
                        provinsi.append(option).trigger('change.select2');
                    }

                    provinsi.val('0').trigger('change.select2');
                }   
            }
        });
    }
});

$('#id_provinsi').change(function(e){
    var $this = $(this)
    var provinsi = $this.val();

    if (provinsi !== null || provinsi.length() > 0){
        $.ajax({
            type: "POST",
            url: '/ajax/akses_dati2/',
            datatype: 'json',
            data: {'provinsi':provinsi},
            success: function (data) {
                if (data){
                    var dati2 = $('#id_dati2');

                    dati2.empty().trigger('change.select2');
    
                    var option = new Option('Pilih Kota', 0, true, true);
                    dati2.append(option).trigger('change.select2');
                    

                    for(var i=0; i < data.length; i++){
                        option = new Option(data[i].fields.nama_dati2, data[i].pk, false, true);
                        dati2.append(option).trigger('change.select2');
                    }

                    dati2.val('0').trigger('change.select2');
                    
                }   
            }
        });
    }
});

$('#id_dati2').change(function(e){
    
    var $this = $(this)
    var dati2 = $this.val();

    if (dati2 !== null || dati2.length() > 0){
        $.ajax({
            type: "POST",
            url: '/ajax/akses_kecamatan/',
            datatype: 'json',
            data: {'dati2':dati2},
            success: function (data) {
                if (data){
                    var kecamatan = $('#id_kecamatan');

                    kecamatan.empty().trigger('change.select2');
    
                    var option = new Option('Pilih Kecamatan', 0, true, true);
                    kecamatan.append(option).trigger('change.select2');
                    

                    for(var i=0; i < data.length; i++){
                        option = new Option(data[i].fields.nama_kecamatan, data[i].pk, false, true);
                        kecamatan.append(option).trigger('change.select2');
                    }

                    kecamatan.val('0').trigger('change.select2');
                    
                }   
            }
        });
    }
});

$('#id_kecamatan').change(function(e){
    
    var $this = $(this)
    var kecamatan = $this.val();

    if (kecamatan !== null || kecamatan.length() > 0){
        $.ajax({
            type: "POST",
            url: '/ajax/akses_kelurahan/',
            datatype: 'json',
            data: {'kecamatan':kecamatan},
            success: function (data) {
                if (data){
                    var kelurahan = $('#id_kelurahan');

                    kelurahan.empty().trigger('change.select2');
    
                    var option = new Option('Pilih Kelurahan', 0, true, true);
                    kelurahan.append(option).trigger('change.select2');
                    

                    for(var i=0; i < data.length; i++){
                        option = new Option(data[i].fields.nama_kelurahan, data[i].pk, false, true);
                        kelurahan.append(option).trigger('change.select2');
                    }

                    kelurahan.val('0').trigger('change.select2');
                    
                }   
            }
        });
    }
});

/*
Wizard Post Registration
*/
var $postRegFinish = $('#id_postreg_wizard').find('ul.pager li.finish'),
	$postRegValidator = $("#id_postreg_wizard form").validate({
	highlight: function(element) {
		$(element).closest('.form-group').removeClass('has-success').addClass('has-error');
	},
	success: function(element) {
		$(element).closest('.form-group').removeClass('has-error');
		$(element).remove();
	},
	errorPlacement: function( error, element ) {
		element.parent().append( error );
	}
});

$('#id_postreg_wizard').bootstrapWizard({
	tabClass: 'wizard-steps',
	nextSelector: 'ul.pager li.next',
	previousSelector: 'ul.pager li.previous',
	firstSelector: null,
	lastSelector: null,
	onNext: function( tab, navigation, index, newindex ) {
		var validated = $('#id_postreg_wizard form').valid();
		if( !validated ) {
			$postRegValidator.focusInvalid();
			return false;
		}
	},
	onTabClick: function( tab, navigation, index, newindex ) {
		if ( newindex == index + 1 ) {
			return this.onNext( tab, navigation, index, newindex);
		} else if ( newindex > index + 1 ) {
			return false;
		} else {
			return true;
		}
	},
	onTabChange: function( tab, navigation, index, newindex ) {
		var $total = navigation.find('li').length - 1;
		
        if (newindex == $total){
            $('#id_postreg_wizard ul.pager li.next').addClass('d-none');
        }else{
            $('#id_postreg_wizard ul.pager li.next').removeClass('d-none');
        };

        $postRegFinish[ newindex != $total ? 'addClass' : 'removeClass' ]( 'd-none' );
        
	},
	onTabShow: function( tab, navigation, index ) {
		var $total = navigation.find('li').length - 1;
		var $current = index;
		var $percent = Math.floor(( $current / $total ) * 100);
			
		navigation.find('li').removeClass('active');
		navigation.find('li').eq( $current ).addClass('active');

		$('#id_postreg_wizard').find('.progress-indicator').css({ 'width': $percent + '%' });
		tab.prevAll().addClass('completed');
		tab.nextAll().removeClass('completed');
	}
});
