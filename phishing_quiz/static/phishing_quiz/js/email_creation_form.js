$(document).ready(function(){
    if(message === 'success'){
        // $.notifyDefaults({
        //         url_target: "_self"
        //     });
        $.notify( 'Email successfully created! Click to return to Home',{
                element: 'body',
               allow_dismiss: false,
               url: "/",
               offset: {
                   y: 80,
                   x: 20
               },
                type: 'success',
            animate: {
                enter: 'animated fadeInRight',
                exit: 'animated fadeOutRight'
            },
            delay: 5000,
        });
    }
    else if(message !== ''){
        $.notify( message,{
                element: 'body',
               allow_dismiss: false,
               url: "/",
               offset: {
                   y: 80,
                   x: 20
               },
                type: 'danger',
            animate: {
                enter: 'animated fadeInRight',
                exit: 'animated fadeOutRight'
            },
            delay: 5000,
        });
    }

    // alert(message);
});