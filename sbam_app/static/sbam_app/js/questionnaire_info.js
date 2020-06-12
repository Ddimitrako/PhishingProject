$(document).ready(function(){

    var statuses = [quest_status];
    var initial_statuses = [quest_status];
    var changes_idxs = [];

    function update_label(selector, op){
        if(op)
            if($("label[for='" + $(selector).attr('id') + "']").text() === 'Active')
                $("label[for='" + $(selector).attr('id') + "']").text('Inactive (Changed)');
            else
                $("label[for='" + $(selector).attr('id') + "']").text('Active (Changed)');
        else
            if($("label[for='" + $(selector).attr('id') + "']").text().startsWith('Active'))
                $("label[for='" + $(selector).attr('id') + "']").text('Inactive');
            else
                $("label[for='" + $(selector).attr('id') + "']").text('Active');
    }

    //function to check if there are any changes on the statuses
    //Toggles visibility of button to prepare the update request
    function update_changes(idx, statuses, initial_statuses, changes_idxs, selector) {
        console.log(selector)
        if (idx === 0) {
            statuses[idx] = statuses[idx] === 1 ? 0 : 1;

            if(!changes_idxs.includes(0)) {
                changes_idxs.push(0);
                update_label(selector, 1);
            }
            if(initial_statuses[0] === statuses[0])
                for(var i=0; i < changes_idxs.length; i++)
                    if(changes_idxs[i] === 0) {
                        changes_idxs.splice(i, 1);
                        update_label(selector, 0);
                    }
        }
        else{
            statuses[idx].status = statuses[idx].status === 1 ? 0 : 1;
            if(!changes_idxs.includes(parseInt(idx))) {
                changes_idxs.push(parseInt(idx));
                update_label(selector, 1);
            }

            if(initial_statuses[idx].status === statuses[idx].status)
                for (var i = 0; i < changes_idxs.length; i++)
                    if (changes_idxs[i] === parseInt(idx)) {
                        changes_idxs.splice(i, 1);
                        update_label(selector, 0);
                    }
        }

        if(JSON.stringify(statuses) === JSON.stringify(initial_statuses)) {
            $('.update-button').hide();
            changes_idxs.length = 0;
        }
        else
            $('.update-button').show();
        return statuses;
    }

    for (let quest_obj in questData) {
        question_data1 = {};
        question_data1['id'] = questData[quest_obj]['question'].id;
        question_data1['status'] = questData[quest_obj]['question'].is_active;
        question_data2 = {};
        question_data2['id'] = questData[quest_obj]['question'].id;
        question_data2['status'] = questData[quest_obj]['question'].is_active;
        statuses.push(question_data1);
        initial_statuses.push(question_data2);
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

    $('.custom-control-input').change(function(){
        if(this.hasAttribute('data-id'))
            statuses = update_changes($(this).attr('data-id'), statuses, initial_statuses, changes_idxs, this);
        else
            statuses = update_changes(0, statuses, initial_statuses, changes_idxs, this);
    });

    $('.update-button').click(function () {
        console.log(statuses);
        console.log(initial_statuses);
        console.log(changes_idxs);
        data = {};
        data['indexes'] = JSON.stringify(changes_idxs);
        data['status'] = JSON.stringify(statuses);
        var csrftoken = getCookie('csrftoken');
        $.ajax({
            type: "POST",
            headers: {"X-CSRFToken": csrftoken},
            dataType: 'json',
            url: '/questionnaires/'+quest_id+'/',
            data: data,
            success: function(response){
                console.log(response);
                $('#questionnaireEditSuccessModal').modal('toggle');
            },
        })
    })
});