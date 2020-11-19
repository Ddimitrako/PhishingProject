$(document).ready(function(){

    // window.onload = function() {
    //   let link = document.createElement("link");
    //   link.href = "/static/phishing_quiz/css/email-template.css";      /**** your CSS file ****/
    //   link.rel = "stylesheet";
    //   link.type = "text/css";
    //   frames[0].document.head.appendChild(link); /**** 0 is an index of your iframe ****/
    // }

    $('#email-1 input').on('change', function (){
        val1 = $('input[name=phishing-email-1]:checked', '#email-1').val();
        // console.log(val1);
        check_input();
    });

     $('#email-2 input').on('change', function (){
        val2 = $('input[name=phishing-email-2]:checked', '#email-2').val();
        // console.log(val2);
        check_input();
    });

      $('#email-3 input').on('change', function (){
        val3 = $('input[name=phishing-email-3]:checked', '#email-3').val();
        // console.log(val3);
        check_input();
    });

    function check_input(){
        val1 = $('input[name=choices]:checked', '#email-1').val();
        val2 = $('input[name=choices]:checked', '#email-2').val();
        val3 = $('input[name=choices]:checked', '#email-3').val();
        console.log(val1);
        console.log(val2);
        console.log(val3);

        if(val1 !== undefined && val2 !== undefined && val3 !== undefined){
            $('.submit-btn').show();
        }
    }

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

    $('#email-1').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        // create_post();
    });
    $('#email-2').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        // create_post();
    });
    $('#email-3').on('submit', function(event){
        event.preventDefault();
        console.log("form submitted!")  // sanity check
        // create_post();
    });

    $('.submit-btn').click(function (){
        var csrftoken = getCookie('csrftoken');
        const ajax_data = {}
        ajax_data['email_1'] = $('input[name=phishing-email-1]:checked', '#email-1').val();
        ajax_data['email_2'] = $('input[name=phishing-email-2]:checked', '#email-2').val();
        ajax_data['email_3'] = $('input[name=phishing-email-3]:checked', '#email-3').val();
        // alert(ajax_data)
        $.ajax({
            "type": "POST",
            headers: {"X-CSRFToken": csrftoken},
            dataType: 'json',
            'url': 'phishing_quiz',
            'data': ajax_data,
        })
    })

});