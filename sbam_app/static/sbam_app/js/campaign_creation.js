$(document).ready(function(){
    console.log(domainstreeData);
    console.log(usertreeData);

    const domainsTree = new Tree('#dim_tree_container', {
        data: domainstreeData,
        closeDepth: 1,

        onChange: function() {
            $("#selected_domains tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            for(var i=0; i < len; i++){
                if (this.selectedNodes[i].id.includes('domain'))
                    $("#selected_domains tbody").append("<tr><th >"+i+"</th><td>"+this.selectedNodes[i].text+"</td></tr>");
            }
        },
    });

    const userTree = new Tree('#user_tree_container', {
        data: usertreeData,

        closeDepth: 1,

        onChange: function() {
            $("#selected_users tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            for(var i=0; i < len; i++){
                if (!this.selectedNodes[i].id.includes('users'))
                    $("#selected_users tbody").append("<tr><th scope=\"row\">"+i+"</th><td>"+this.selectedNodes[i].text+"</td></tr>");
            }
        },
    });

    const testsTree = new Tree('#tests_tree_container', {
        data: testTreeData,
        closeDepth: 1,

        onChange: function() {
            $("#selected_tests tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            for(var i=0; i < len; i++){
                // if (this.selectedNodes[i].id.includes('domain'))
                $("#selected_tests tbody").append("<tr><th >"+i+"</th><td>"+this.selectedNodes[i].text+"</td></tr>");
            }
        },
    });

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

    $('#id_start_date').datetimepicker('minDate', [''+new Date().getFullYear()+'-'+(new Date().getMonth()+1)+'-'+new  Date().getDate()+'']);
    $('#id_end_date').datetimepicker('minDate', [''+new Date().getFullYear()+'-'+(new Date().getMonth()+1)+'-'+new  Date().getDate()+'']);


    $('#create_campaign_btn').click(function () {

        const start_date = $('#id_start_date').val();
        const end_date = $('#id_end_date').val();
        if(end_date < start_date)
            alert("Incorrect date input")
        const ajax_data = {};
        var csrftoken = getCookie('csrftoken');
        const domain_len = domainsTree.selectedNodes.length;
        const domains = [];
        for(var i=0; i < domain_len; i++){
            if (domainsTree.selectedNodes[i].id.includes('domain')) {
                console.log(domainsTree.selectedNodes[i])
                domains.push(domainsTree.selectedNodes[i]);
            }
        }

        const usr_len = userTree.selectedNodes.length;
        const users = [];
        for(var i=0; i < usr_len; i++){
            if (!userTree.selectedNodes[i].id.includes('users'))
                users.push(userTree.selectedNodes[i]);
        }

        const test_len = testsTree.selectedNodes.length;
        const tests = [];
        for(var i=0; i < test_len; i++){
            // if (!userTree.selectedNodes[i].id.includes('users'))
                tests.push(testsTree.selectedNodes[i]);
        }


        ajax_data["start_date"] = start_date;
        ajax_data["end_date"] = end_date;
        ajax_data["domains"] = JSON.stringify(domains);
        ajax_data["users"] =  JSON.stringify(users);
        ajax_data["tests"] =  JSON.stringify(tests);
        // data = JSON.stringify(ajax_data);
        console.log('Sto Ajax call');
        // console.log(data);
        $.ajax({
            "type": "POST",
            headers: { "X-CSRFToken": csrftoken },
            dataType: 'json',
            // 'url': 'create_campaign/',
            'data': ajax_data,
            success: function(result){
                console.log(result)
            }
        })
    })
});