$(document).ready(function(){
    console.log(questtreeData);
    console.log(usertreeData);
    console.log(testTreeData);

    const questTree = new Tree('#dim_tree_container', {
        data: questtreeData,
        closeDepth: 1,

        onChange: function() {
            document.getElementById("selected_domains").deleteTHead();
            $("#selected_domains tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            if(len > 0) {
                $("#selected_domains").append("<thead class=\"thead-dark\">\n" +
                    "    <tr>\n" +
                    "      <th class='sel_index'>#</th>\n" +
                    "      <th class='sel_index'>Name</th>\n" +
                    "      <th class='sel_index'>Type</th>\n" +
                    "    </tr>\n" +
                    "  </thead>");
                $('.sel-quest-par').hide();
            }
            else
                $('.sel-quest-par').show();

            let quest_level = '';
            let idx = 1;
            for(var i=0; i < len; i++){
                if (this.selectedNodes[i].id.includes('quest')) {
                    $("#selected_domains tbody").append("<tr><th class='sel_index'>" + idx + "</th><td style='width: 80%'>" + this.selectedNodes[i].text + "" +
                        "</td><td>" + quest_level + "</td></tr>");
                    idx++;
                }


                if (this.selectedNodes[i].id.includes('indv') || this.selectedNodes[i].id.includes('org')) {
                    if (this.selectedNodes[i].attributes.level === 0)
                        quest_level = 'Org';
                    else
                        quest_level = 'Indiv';
                }

                // if (this.selectedNodes[i].id.includes('quest'))
                //         $("#selected_domains tbody").append("<tr><th class='sel_index'>"+i+"</th><td style='width: 80%'>"+this.selectedNodes[i].text+"" +
                //             "</td>"+ quest_level +"<td></td></tr>");
            }
        },
    });


    const userTree = new Tree('#user_tree_container', {
        data: usertreeData,

        closeDepth: 1,

        onChange: function() {
            // $("#selected_users").delete
            document.getElementById("selected_users").deleteTHead();
            $("#selected_users tr").remove();
            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            if(len > 0) {
                $("#selected_users").append("<thead class=\"thead-dark\">\n" +
                    "    <tr>\n" +
                    "      <th class='sel_index'>#</th>\n" +
                    "      <th class='sel_index'>Name</th>\n" +
                    "      <th class='sel_index'>Type</th>\n" +
                    "    </tr>\n" +
                    "  </thead>");

                $('.sel-usr-par').hide();
            }
            else
                $('.sel-usr-par').show();


            for(var i=0; i < len; i++){
                if (!this.selectedNodes[i].id.includes('users')) {
                    if(this.selectedNodes[i].id.includes('user'))
                        $("#selected_users tbody").append("<tr><th class='sel_index'>" + i + "</th><td style='width: 80%'>" + this.selectedNodes[i].text + "</td><td style='width: 20%'>User</td></tr>");
                    else
                        $("#selected_users tbody").append("<tr><th class='sel_index'>" + i + "</th><td style='width: 80%'>" + this.selectedNodes[i].text + "</td><td style='width: 20%'>Group</td></tr>");
                }
            }
        },
    });

    console.log(testTreeData.length);
    let testsTree;

    testsTree = new Tree('#tests_tree_container', {
        data: testTreeData,
        closeDepth: 1,

        onChange: function () {
            document.getElementById("selected_tests").deleteTHead();
            $("#selected_tests tr").remove();
            var len = this.selectedNodes.length;
            if(len > 0) {
                $("#selected_tests").append("<thead class=\"thead-dark\">\n" +
                    "    <tr>\n" +
                    "      <th class='sel_index'>#</th>\n" +
                    "      <th class='sel_index'>Name</th>\n" +
                    "    </tr>\n" +
                    "  </thead>");

                $('.sel-tests-par').hide();
            }
            else
                $('.sel-tests-par').show();

            console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            for (var i = 0; i < len; i++) {
                if (this.selectedNodes[i].id.includes('test'))
                    $("#selected_tests tbody").append("<tr><th class='sel_index'>" + i + "</th><td style='width: 70%'>" + this.selectedNodes[i].text + "</td></tr>");
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

    $('#id_start_date').datetimepicker('minDate', [new Date().getFullYear()+'-'+(new Date().getMonth()+1)+'-'+new Date().getDate()]);
    $('#id_end_date').datetimepicker('minDate', [new Date().getFullYear()+'-'+(new Date().getMonth()+1)+'-'+new Date().getDate()]);

    //    controlling the expansion level of the tree one level at a time
    $('#dim_tree_container li').addClass('treejs-node__close');

    //    Function to check if the dates are valid -> end_date > start_date
    function check_campaign_dates(){
        const start_date = $('#id_start_date').val();
        const end_date = $('#id_end_date').val();
        if(start_date === ''){
            alert("Please enter your campaign start date");
            return 0;
        }
        if(end_date === ''){
            alert("Please enter your campaign end date");
            return 0;
        }
        if(end_date < start_date) {
            alert("End date should be greater than the start date of your campaign");
            return 0;
        }
        return 1;
    }

    //    Function to validate that a questionnaire or a test is selected
    function check_selected_items(){
        if(questTree.selectedNodes.length === 0 ){            //----> Thumisou oti prepei na baleis kai to if kai gia ta test
            alert('Please select a Questionnaire or a Test');
            return 0;
        }
        if(userTree.selectedNodes.length === 0) {
            alert('Please select a user or a group to assign the campaign');
            return 0;
        }
        return 1;
    }



    $('#create_campaign_btn').click(function () {

        if(check_campaign_dates() && check_selected_items()){
            const title = $('#id_title').val();
            const start_date = $('#id_start_date').val();
            const end_date = $('#id_end_date').val();
            const ajax_data = {};
            var csrftoken = getCookie('csrftoken');
            const domain_len = questTree.selectedNodes.length;
            const domains = [];
            for(var i=0; i < domain_len; i++){
                if (questTree.selectedNodes[i].id.includes('quest')) {
                    // console.log(domainsTree.selectedNodes[i]);
                    domains.push(questTree.selectedNodes[i]);
                }
            }

            const usr_len = userTree.selectedNodes.length;
            const users = [];
            for(var i=0; i < usr_len; i++){
                if (!userTree.selectedNodes[i].id.includes('users'))
                    users.push(userTree.selectedNodes[i]);
            }

            const tests = [];
            if (testTreeData.length > 1) {
                const test_len = testsTree.selectedNodes.length;

                for (var i = 0; i < test_len; i++) {
                    tests.push(testsTree.selectedNodes[i]);
                }
            }

            ajax_data["title"] = title;
            ajax_data["start_date"] = start_date;
            ajax_data["end_date"] = end_date;
            ajax_data["quests"] = JSON.stringify(domains);
            ajax_data["users"] =  JSON.stringify(users);
            ajax_data["tests"] =  JSON.stringify(tests);

            // console.log('Sto Ajax call');
            // console.log(ajax_data);
            $.ajax({
                "type": "POST",
                headers: { "X-CSRFToken": csrftoken },
                dataType: 'json',
                // 'url': 'create_campaign/',
                'data': ajax_data,
                success: function(response){
                    console.log(response);
                    $('#campaignSuccessModal').modal('toggle');
                },
                error : function(response){
                    console.log(response);
                    $('#campaignErrorModal').modal('toggle');
                }
            })
        }
    })
});