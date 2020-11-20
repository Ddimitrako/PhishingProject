$(document).ready(function(){


    let carousel = $("#carouselExampleIndicators").carousel();
    let answers = {};
    let compl_rate = (1 / emails_num) * 100;

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

    $(".btn-group > button.btn").on("click", function(){
        carousel.carousel('next');
        answers['email_'+$(this).attr('data-email')] = $(this).attr('data-value');
        console.log(answers);
        $('.progress-bar').css('width', (compl_rate+((1/emails_num)*100))+'%').attr('aria-valuenow', (compl_rate+((1/emails_num)*100)));
        compl_rate += (1/emails_num)*100;

        $('.prog-indicator').text('Email ' + (++current_num) + ' of '+(emails_num));
        // console.log($(this).attr('data-value') + ' '+ emails_num.toString());
        if($(this).attr('data-email') === emails_num.toString()){

            submit_answers();
        }
    });

    function submit_answers(){
        alert('edw')
        var csrftoken = getCookie('csrftoken');
        let results = {};
        results['data'] =  JSON.stringify(answers);
        $.ajax({
            type: "POST",
            headers: {"X-CSRFToken": csrftoken},
            dataType: 'json',
            url: 'phishing_quiz',
            data: results,
            success: function (result) {
               alert('gurisaaa');
            }
        })
    }

});