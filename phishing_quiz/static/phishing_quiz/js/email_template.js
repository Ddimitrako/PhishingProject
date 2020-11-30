$(document).ready(function(){
    $('a').each(function(){
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'top');
        $(this).attr('title', $(this).attr('href'));
        $(this).tooltip();
    })

    $('img').each(function(){
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'top');
        $(this).attr('title', $(this).attr('href'));
        $(this).tooltip();
    })

    let color_list = ['#4285F4', '#BB001B', '#EA4335', '#FBBC05', '#34A853'];

    $('.dot').css('background-color', color_list[Math.floor(Math.random() * color_list.length)])

});