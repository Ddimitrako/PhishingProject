$(document).ready(function(){
    //console.log(questtreeData);
    //console.log(usertreeData);
    //console.log(testTreeData);

    const questTree = new Tree('#dim_tree_container', {
        data: questtreeData,
        closeDepth: 1,

        onChange: function() {
            document.getElementById("selected_domains").deleteTHead();
            $("#selected_domains tr").remove();
            //console.log(this.selectedNodes);
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


    let userTree = null;
    //console.log(usertreeData);
    if(usertreeData[1].children.length > 0){
        userTree = new Tree('#user_tree_container', {
            data: usertreeData,

            closeDepth: 1,

            onChange: function() {
                // $("#selected_users").delete
                $('#id_label_multiple').val(null).trigger('change');
                document.getElementById("selected_users").deleteTHead();
                $("#selected_users tr").remove();
                //console.log(this.selectedNodes);
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

                let ids = [];
                for(var i=0; i < len; i++){

                    if (!this.selectedNodes[i].id.includes('users')) {
                        if(this.selectedNodes[i].id.includes('user'))
                            $("#selected_users tbody").append("<tr><th class='sel_index'>" + i + "</th><td style='width: 80%'>" + this.selectedNodes[i].text + "</td><td style='width: 20%'>User</td></tr>");
                        else
                            $("#selected_users tbody").append("<tr><th class='sel_index'>" + i + "</th><td style='width: 80%'>" + this.selectedNodes[i].text + "</td><td style='width: 20%'>Group</td></tr>");
                        var data = {
                            id: this.selectedNodes[i].id,
                            text: this.selectedNodes[i].text
                        };
                         var newOption = new Option(data.text, data.id, false, false);
                        $('#id_label_multiple').append(newOption).trigger('change');
                        ids.push(this.selectedNodes[i].id);
                    }
                }
                $('#id_label_multiple').val(ids);
            },
        });
    }

    if(testTreeData.length > 0)
        $(".tests_avail").hide()
    const testsTree = new Tree('#tests_tree_container', {
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
                    "      <th class='sel_index'></th>\n" +
                    "    </tr>\n" +
                    "  </thead>");

                $('.sel-tests-par').hide();
            }
            else
                $('.sel-tests-par').show();

            //console.log(this.selectedNodes);
            var len = this.selectedNodes.length;
            let idx = 1;
            for (var i = 0; i < len; i++) {
                if (this.selectedNodes[i].id.includes('test')) {
                    if(this.selectedNodes[i].text === 'Phishing Email Test'){
                         // $('#edit_phishing_test').show();
                         $("#selected_tests tbody").append("<tr><th class='sel_index'>" + idx + "</th><td style='width: 70%'>"
                        + this.selectedNodes[i].text + "</td><td style='width: 30%'>" +
                             "<button type='button' onclick='toggleSimModal();' class='btn btn-primary btn-xs float-right' id='edit_phishing_test'" +
                             " title='Edit Phishing Test'>Edit</button></td></tr>");

                    }
                    else if (this.selectedNodes[i].text === 'Phishing Email Quiz'){
                        $("#selected_tests tbody").append("<tr><th class='sel_index'>" + idx + "</th><td style='width: 70%'>"
                        + this.selectedNodes[i].text + "</td><td style='width: 30%'>" +
                             "<button type='button' onclick='toggleQuizModal();' class='btn btn-primary btn-xs float-right' id='edit_phishing_quiz'" +
                             " title='Edit Phishing Quiz'>Edit</button></td></tr>");
                    }
                    else {

                        $("#selected_tests tbody").append("<tr><th class='sel_index'>" + idx + "</th><td style='width: 70%'>"
                            + this.selectedNodes[i].text + "</td><td></td></tr>");
                    }

                    idx++;
                }
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
        let questselected = false;
        let testselected = false;
        for (var i = 0; i < questTree.selectedNodes.length; i++){
            if(questTree.selectedNodes[i].id.includes('quest'))
                questselected = true;
        }
        if(testsTree != null){
            for (var i = 0; i < testsTree.selectedNodes.length; i++){
                if(testsTree.selectedNodes[i].id.includes('test'))
                    testselected = true;
            }
        }
        if(!questselected && !testselected){
            alert('Please select a Questionnaire or a Test');
            return 0;
        }
        if(userTree.selectedNodes.length === 0) {
            alert('Please select a user or a group to assign the campaign');
            return 0;
        }
        return 1;
    }


    function loadIframe(url) {
        var $iframe = $('#ifrm');
        if ( $iframe.length ) {
            $iframe.attr('src','/sim_email/'+url);
            return false;
        }
        return true;
    }

    function loadIframeQuiz(url) {
        var $iframe = $('#ifrm_quiz');
        if ( $iframe.length ) {
            $iframe.attr('src','/email_request/'+url);
            return false;
        }
        return true;
    }


    $('a[data-toggle="list"]').on('show.bs.tab', function (e) {
        e.target // newly activated tab
        e.relatedTarget // previous active tab
        // alert('edw');
        selected_email_id = $(e.target).data('id');
        // console.log($(e.target).data('id'));
        // console.log(selected_email_id);
        loadIframe($(e.target).data('id'));

    })


    $(".phish_email:input:checkbox").each(function (index){
        this.checked = (".phish_email:input:checkbox" < 5);
    }).change(function (){

        if ($(".phish_email:input:checkbox:checked").length > 5){
            this.checked = false;
            toastr["info"]("Maximum number of emails reached. Unselect an email to insert a new one")
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
        else{
            let counter = $(".phish_email:input:checkbox:checked").length;
            $('.selected_phish_emails_counter').text(counter + '/5');
        }
        loadIframeQuiz($(this).val());
    });

    function check_campaign_title(){
        let campaign_title = $('#id_title').val();
        if(campaign_title === '') {
            alert('Please fill in the campaign title');
            return 0;
        }
        return 1;
    }

    function check_selected_emails(){
        selected_tests = testsTree.selectedNodes;

        for(var i=0; i< selected_tests.length; i++){
            if(selected_tests[i].text === 'Phishing Email Quiz'){
                if($(".phish_email:input:checkbox:checked").length === 0){
                    alert('Please insert at least 1 email at Phishing email Quiz');
                    return 0;
                }
            }
        }
        return 1;
    }

    function check_sim_email_sel() {
        selected_tests = testsTree.selectedNodes;

        for (var i = 0; i < selected_tests.length; i++) {
            if (selected_tests[i].text === 'Phishing Email Test') {
                if (selected_email_id === -1) {
                    alert('Please choose an email for the Phishing Email Test');
                    return 0;
                }
            }
        }
        return 1;
    }

    $('#edit_phishing_test').click(function (){
         $('#PhishingTestModal').modal('toggle');
    })


    //send email to check  ajax
    $('.email-check').click(function () {
        // alert(selected_email_id);
        const ajax_data = {};
        var csrftoken = getCookie('csrftoken');
        ajax_data["email_id"] = selected_email_id;
        $.ajax({
                "type": "POST",
                headers: { "X-CSRFToken": csrftoken },
                dataType: 'json',
                'url': './../check_email/',
                'data': ajax_data,
                success: function(response, status, xhr){
                    //console.log(response);

                    if(response['success'] === 'True'){
                        // console.log(response);
                        // alert('edww');
                        toastr["success"]("Email sent successfully!")

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
                },
                error : function(response){
                    toastr["error"]("Email did not sent!")

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
            })
    })


    //    campaign creation ajax
    $('#create_campaign_btn').click(function () {

        if(check_campaign_dates() && check_selected_items() && check_campaign_title() && check_selected_emails() && check_sim_email_sel()){
            const title = $('#id_title').val();
            const start_date = $('#id_start_date').val();
            const end_date = $('#id_end_date').val();
            const descr = $('#id_description').val()
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
                    // alert('edw');
                    if(testsTree.selectedNodes[i].text === 'Phishing Email Quiz'){
                        $.each($(".phish_email:input:checkbox:checked"), function (){
                            // console.log($(this).val());
                            selected_phish_emails.push($(this).val());
                        })
                    }
                }
            }


            ajax_data["title"] = title;
            ajax_data["start_date"] = start_date;
            ajax_data["end_date"] = end_date;
            ajax_data["description"] = descr;
            ajax_data["quests"] = JSON.stringify(domains);
            ajax_data["users"] =  JSON.stringify(users);
            ajax_data["tests"] =  JSON.stringify(tests);
            ajax_data["email_id"] = selected_email_id;
            ajax_data["phishing_emails"] =  JSON.stringify(selected_phish_emails);

            //console.log('Sto Ajax call');
            // console.log(ajax_data);
            $.ajax({
                "type": "POST",
                headers: { "X-CSRFToken": csrftoken },
                dataType: 'json',
                // 'url': 'create_campaign/',
                'data': ajax_data,
                success: function(response){
                    //console.log(response);
                    $('#campaignSuccessModal').modal('toggle');
                },
                error : function(response){
                    //console.log(response);
                    $('#campaignErrorModal').modal('toggle');
                }
            })
        }
    })
});