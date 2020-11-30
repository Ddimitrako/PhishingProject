$(document).ready(function(){
    $('a').each(function(){
        $(this).attr('data-toggle', 'tooltip');
        $(this).attr('data-placement', 'right');
        $(this).attr('title', $(this).attr('href'));
    })
});