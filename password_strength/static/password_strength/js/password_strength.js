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

    $('.pass-form-submit').click(function (){
        // alert('edw');
        var csrftoken = getCookie('csrftoken');
        const ajax_data = {}
        ajax_data["pass_1"] = $('#id_pass_1').val();
        ajax_data["pass_2"] = $('#id_pass_2').val();
        ajax_data["pass_3"] = $('#id_pass_3').val();
        // console.log(ajax_data);
        if(ajax_data["pass_1"] !== '' && ajax_data["pass_2"] !== '' && ajax_data["pass_3"] !== '') {
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
                        $('.'+pass+'_score').append(response['data'][pass]['score'] + '/10');
                        $('.'+pass+'_crack_display').append(response['data'][pass]['crack_display']);
                        sugesstions_string = '<ul>';
                        for(sugg in response['data'][pass]['suggestions']){
                            sugesstions_string += '<li>'
                                + response['data'][pass]['suggestions'][sugg]
                                + '</li>'
                        }
                        sugesstions_string += '</ul>'
                        $('.'+pass+'_suggestions').append(sugesstions_string);
                    }
                    $('.total_score').append(response['total_score'].toFixed(2) + '/10');
                    // alert('pali edw');
                },
            })
        }
    })
});