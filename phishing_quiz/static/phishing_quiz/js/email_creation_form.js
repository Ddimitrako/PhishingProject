$(document).ready(function(){
    if(message === 'success'){
        toastr["success"]("Your email was successfully created! Now you can return to the Dashboard")

        toastr.options = {
              "closeButton": true,
              "debug": false,
              "newestOnTop": false,
              "progressBar": false,
              "positionClass": "toast-top-right",
              "preventDuplicates": false,
              "onclick": null,
              "showDuration": "300",
              "hideDuration": "1000",
              "timeOut": "5000",
              "extendedTimeOut": "1000",
              "showEasing": "swing",
              "hideEasing": "linear",
              "showMethod": "fadeIn",
              "hideMethod": "fadeOut"
        }

        $('#submit-id-submit').hide();
    }
    else if(message !== ''){

        toastr["error"](message)

        toastr.options = {
              "closeButton": true,
              "debug": false,
              "newestOnTop": false,
              "progressBar": false,
              "positionClass": "toast-top-right",
              "preventDuplicates": false,
              "onclick": null,
              "showDuration": "300",
              "hideDuration": "1000",
              "timeOut": "5000",
              "extendedTimeOut": "1000",
              "showEasing": "swing",
              "hideEasing": "linear",
              "showMethod": "fadeIn",
              "hideMethod": "fadeOut"
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



    $('input[name="email_file"]').change(function() {
        if ($('#id_email_file')[0].files.length === 0) {
            console.log("No files selected");
        }
        else {

            var fd = new FormData();
            console.log($('#id_email_file')[0].files[0].name);
            fd.append('email_file',$('#id_email_file')[0].files[0], $('#id_email_file')[0].files[0].name);
            fd.append('title','');
            fd.append('subject','');

            console.log(fd);
            var csrftoken = getCookie('csrftoken');

            $.ajax({
                url: 'sim_endpoint_preview/',
                type: 'post',
                headers: { "X-CSRFToken": csrftoken },
                data: fd,
                contentType: false,
                processData: false,
                success: function(response){
                    if(response['success'] === 'True'){
                        console.log(response['msg']);
                        $('.preview').text('')
                        $('.preview').append(response['msg'])
                    }
                    else{
                        alert('file not uploaded');
                    }
                },
            });
            console.log("Some file is selected");

        }
    })


    $('.clipboard').click( function (){
        // alert('edw')
        var copyText = document.getElementById("id_encrypted_link");
        console.log(copyText)
        /* Select the text field */
        copyText.select();
        copyText.setSelectionRange(0, 99999); /* For mobile devices */

        /* Copy the text inside the text field */
        document.execCommand("copy");
    })


});