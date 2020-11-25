$(document).ready(function(){


    let carousel = $("#carouselExampleIndicators").carousel();
    let answers = {};
    let compl_rate = (1 / emails_num) * 100;
    let answers_num = 0;

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

    $('.next-btn').on('click', function(){
        carousel.carousel('next');
        ++current_num;
        $('.prog-indicator').text('Email ' + current_num + ' of '+(emails_num));
        if(current_num === emails_num) {
            $('.next-btn').hide();
            $('.prev-btn').show();
        }
        else
            $('.prev-btn').show();
    });

    $('.prev-btn').on('click', function(){
        carousel.carousel('prev');
        $('.next-btn').show();
        --current_num;
        $('.prog-indicator').text('Email ' + current_num + ' of '+(emails_num));
        if(current_num === 1) {
            $('.prev-btn').hide();
            $('.next-btn').show();
        }
        else
            $('.next-btn').show();
    });

    $(".btn-group > button.btn").on("click", function(){

        if(current_num > 1)
            $('.prev-btn').show();

        if(!('email_'+$(this).attr('data-email') in answers))
            answers_num++;
        
        answers['email_'+$(this).attr('data-email')] = {};
        answers['email_'+$(this).attr('data-email')]['answer'] = $(this).attr('data-value') === 'Phishing_email';
        answers['email_'+$(this).attr('data-email')]['id'] = $(this).attr('data-email');
        console.log(answers);


        $(this).removeClass('btn-outline-info');
        $(this).addClass('btn-info');

        //checking if the eamil is already answered and changes the indicators
        let answer =  $(this).attr('data-value') === 'Phishing_email' ? 'Legit_email' : 'Phishing_email';
        let email_id = $(this).attr('data-email');
        if($(`.btn[data-email=${email_id}][data-value=${answer}]`).hasClass('btn-info')){
            $(`.btn[data-email=${email_id}][data-value=${answer}]`).removeClass('btn-info');
            $(`.btn[data-email=${email_id}][data-value=${answer}]`).addClass('btn-outline-info');
        }

        if(current_num < emails_num){
            carousel.carousel('next');
            $('.progress-bar').css('width', (compl_rate+((1/emails_num)*100))+'%').attr('aria-valuenow', (compl_rate+((1/emails_num)*100)));
            compl_rate += (1/emails_num)*100;

            $('.prog-indicator').text('Email ' + (++current_num) + ' of '+(emails_num));
        }


        if(current_num > 1)
            $('.prev-btn').show();

        if(current_num === emails_num)
            $('.next-btn').hide();

        if(answers_num === emails_num )
            $('.submit-btn').show();

    });

    $('.submit-btn').on('click', function (){
        submit_answers();
    })

    function submit_answers(){
        // alert('edw')
        var csrftoken = getCookie('csrftoken');
        let results = {};
        results['data'] =  JSON.stringify(answers);
        $.ajax({
            type: "POST",
            headers: {"X-CSRFToken": csrftoken},
            dataType: 'json',
            url: 'phishing_quiz',
            data: results,
            success: function (response) {
               $('#phishing_quiz_modal').modal('toggle');
               $('.badge').addClass(response['score_badge']);
               $('.badge').text(response['score'].toFixed(2) + '%');

            }
        })
    }

});