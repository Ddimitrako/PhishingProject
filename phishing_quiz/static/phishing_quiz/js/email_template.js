$(document).ready(function(){
    $('a').each(function(){
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'top');
        $(this).attr('title', $(this).attr('href'));
        $(this).tooltip();
    })
});