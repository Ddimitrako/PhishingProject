$(document).ready(function(){
    // $('.card-info-btn').click(function(){
    //     $(this).text(function(i,old){
    //         return old=='Read More' ?  'Read Less' : 'Read More';
    //     });
    // });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    $('#pass-form').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        // create_post();
    });

    $('input[name="pass_1_confirm"]').blur(function() {
        var pass = $('#id_pass_1').val();
        var repass = $('#id_pass_1_confirm').val();
        console.log(pass);
        console.log(repass);
        if(($('#id_pass_1').val().length == 0) || ($('#id_pass_1_confirm').val().length == 0)){
            $('#id_pass_1').addClass('form-control is-invalid');
        }
        else if (pass != repass) {
            $('#id_pass_1').addClass('form-control is-invalid');
            $('#id_pass_1_confirm').addClass('form-control is-invalid');
        }
        else {
            $('#id_pass_1').removeClass().addClass('form-control is-valid');
            $('#id_pass_1_confirm').removeClass().addClass('form-control is-valid');
        }
    });

    $('input[name="pass_2_confirm"]').blur(function() {
        var pass = $('#id_pass_2').val();
        var repass = $('#id_pass_2_confirm').val();
        console.log(pass);
        console.log(repass);
        if(($('#id_pass_2').val().length == 0) || ($('#id_pass_2_confirm').val().length == 0)){
            $('#id_pass_1').addClass('form-control is-invalid');
        }
        else if (pass != repass) {
            $('#id_pass_2').addClass('form-control is-invalid');
            $('#id_pass_2_confirm').addClass('form-control is-invalid');
        }
        else {
            $('#id_pass_2').removeClass().addClass('form-control is-valid');
            $('#id_pass_2_confirm').removeClass().addClass('form-control is-valid');
        }
    });

    $('input[name="pass_3_confirm"]').blur(function() {
        var pass = $('#id_pass_3').val();
        var repass = $('#id_pass_3_confirm').val();
        console.log(pass);
        console.log(repass);
        if(($('#id_pass_3').val().length == 0) || ($('#id_pass_3_confirm').val().length == 0)){
            $('#id_pass_3').addClass('form-control is-invalid');
        }
        else if (pass != repass) {
            $('#id_pass_3').addClass('form-control is-invalid');
            $('#id_pass_3_confirm').addClass('form-control is-invalid');
        }
        else {
            $('#id_pass_3').removeClass().addClass('form-control is-valid');
            $('#id_pass_3_confirm').removeClass().addClass('form-control is-valid');
        }
    });

    $('.close').click(function (){
        $('.pass_1_password').empty();
        $('.pass_2_password').empty();
        $('.pass_3_password').empty();
        $('.pass_1_score').empty();
        $('.pass_2_score').empty();
        $('.pass_3_score').empty();
        $('.pass_1_crack_display').empty();
        $('.pass_2_crack_display').empty();
        $('.pass_3_crack_display').empty();
        $('.total_score').empty();
        $('.pass_1_suggestions').empty();
        $('.pass_2_suggestions').empty();
        $('.pass_3_suggestions').empty();
    })

    function check_form(){

        let alert_string = '';
        let pass_1 = $('#id_pass_1').val();
        let pass_2 = $('#id_pass_2').val();
        let pass_3 = $('#id_pass_3').val();

        let pass_1_confirm = $('#id_pass_1_confirm').val();
        let pass_2_confirm = $('#id_pass_2_confirm').val();
        let pass_3_confirm = $('#id_pass_3_confirm').val();

        if(pass_1 !== pass_1_confirm){
            alert_string += 'Password 1 fields do not match'
        }
        if(pass_2 !== pass_2_confirm){

            alert_string ? alert_string+= '\nPassword 2 fields do not match' : 'Password 2 fields do not match'
        }
        if(pass_3 !== pass_3_confirm){
            alert_string ? alert_string+= '\nPassword 3 fields do not match' : 'Password 3 fields do not match'
        }

        if(alert_string !== ''){
            alert(alert_string);
            return 0;
        }
        else return 1;

    }

    function check_length(){
        let pass_1 = $('#id_pass_1').val();
        let pass_2 = $('#id_pass_2').val();
        let pass_3 = $('#id_pass_3').val();

        let pass_1_confirm = $('#id_pass_1_confirm').val();
        let pass_2_confirm = $('#id_pass_2_confirm').val();
        let pass_3_confirm = $('#id_pass_3_confirm').val();

        if(pass_1.length >= 8 && pass_2.length >= 8 && pass_3.length >= 8 && pass_1_confirm.length >= 8 && pass_2_confirm.length >= 8 && pass_3_confirm.length >= 8)
            return 1
        else return 0
    }

    $('.pass-form-submit').click(function (){
        // alert('edw');
        var csrftoken = getCookie('csrftoken');
        const ajax_data = {}
        ajax_data["pass_1"] = $('#id_pass_1').val();
        ajax_data["pass_2"] = $('#id_pass_2').val();
        ajax_data["pass_3"] = $('#id_pass_3').val();
        // console.log(ajax_data);
        if(check_form() && check_length()){
            if(ajax_data["pass_1"] !== '' && ajax_data["pass_2"] !== '' && ajax_data["pass_3"] !== '') {
                ajax_data['ass_id'] = ass_id;
                $.ajax({
                    "type": "POST",
                    headers: {"X-CSRFToken": csrftoken},
                    dataType: 'json',
                    'url': 'password_strength',
                    'data': ajax_data,
                    success: function (response) {
                        console.log(response);
                        $('#password_strength_modal').modal('toggle');
                        // alert(response['data']);
                        for (pass in response['data']) {
                            console.log(pass);
                            console.log(response['data'][pass]);
                            console.log('.'+pass+'_password');
                            $('.'+pass+'_badge').addClass(response['data'][pass]['badge']);
                            $('.'+pass+'_badge').text(response['data'][pass]['score'].toFixed(2) + '%');
                            $('.'+pass+'_crack_display').append(response['data'][pass]['crack_display']);
                            $('.'+pass+'_weakness_factor').append(response['data'][pass]['weakness_factor'].toFixed(3));
                            sugesstions_string = '<ul>';
                            for(sugg in response['data'][pass]['suggestions']){
                                sugesstions_string += '<li>'
                                    + response['data'][pass]['suggestions'][sugg]
                                    + '</li>'
                            }
                            sugesstions_string += '</ul>'
                            $('.'+pass+'_suggestions').append(sugesstions_string);
                        }
                        $('.badge').addClass(response['total_score_badge']);
                        $('.badge').text(response['total_score'].toFixed(2) + '%');
                        // alert('pali edw');
                    },
                })
            }
        }
    })
});