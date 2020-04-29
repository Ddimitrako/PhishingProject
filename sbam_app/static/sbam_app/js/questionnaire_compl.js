$(document).ready(function(){
     console.log(questData);
    Survey
    .StylesManager
    .applyTheme("modern");


    Survey
    .Serializer
    .addProperty("question", {
        option_id: "tag:number",
        default: 0,
        category: "general"
    });


    //  function responsible for creating boolean questions json for survey
    function create_bool_quest(text, quest_id, question_opt_ids){
        question_obj = {};
        question_obj = {
            type: "boolean",
            name: "question_"+quest_id,
            title: 'Please answer the question',
            label: text,
            isRequired: true,
            valueTrue: question_opt_ids[0],
            valueFalse: question_opt_ids[1]

        };
        return [question_obj];
    }

    //**********************************************************************
    //*** HERE IMPLEMENT ALL FUNCTIONS FOR DIFFERENT TYPES OF QUESTIONS  ***
    //**********************************************************************

    //  function responsible for creating boolean questions json for survey
    function create_perc_quest(text, quest_id, question_opt, colnum){
        choices_list = [];
        let i = 0;
        for(opt in question_opt){

            choices_list.push({
                text: question_opt[opt].text,
                value:question_opt[opt].id
            });
            i++;
        }
        console.log(choices_list);
        question_obj = {};
        question_obj = {
            type: "radiogroup",
            name: "question_"+quest_id,
            title: text,
            // description: text,
            colCount: colnum,
            isRequired: true,
            choices: choices_list

        };
        return [question_obj];
    }

    function create_multiple_opt_quest(text, quest_id, question_opt, colnum){
        choices_list = [];
        for(opt in question_opt){

            choices_list.push({
                text: question_opt[opt].text,
                value:question_opt[opt].id
            });
        }
        console.log(choices_list);
        question_obj = {};
        question_obj = {
            type: "checkbox",
            name: "question_"+quest_id,
            title: text,
            // description: text,
            colCount: colnum,
            isRequired: true,
            choices: choices_list

        };
        return [question_obj];
    }


    //Gathers all questions of survey and creates appropriate json object for each question
    function create_questions_list(){
        questions = [];
        question_obj = {};

        question_obj['questions'] = [];
        questions.push(question_obj);

        for(let quest_obj in questData){
            // console.log(quest_obj, questData[quest_obj]);
            if(quest_obj !== 'title') {
                for (let obj in questData[quest_obj]) {
                    var text;
                    var quest_id;
                    // console.log(obj, questData[quest_obj][obj]);
                    if (questData[quest_obj][obj].hasOwnProperty('text')) {
                        text = questData[quest_obj][obj].text;
                        quest_id = questData[quest_obj][obj].id;
                    }

                    if (questData[quest_obj][obj].hasOwnProperty('type')) {
                        survey_quest = {};
                        if(questData[quest_obj][obj].type === 'BOOL'){
                            question_opt_ids = [];
                            for(opt in questData[quest_obj][2])
                                question_opt_ids.push(questData[quest_obj][2][opt].id);

                            survey_quest['questions'] = create_bool_quest(text, quest_id, question_opt_ids);
                        }
                        else if(questData[quest_obj][obj].type === 'PERC10' || questData[quest_obj][obj].type === 'PERC20'){
                            question_opt = [];
                            for(opt in questData[quest_obj][2])
                                question_opt.push(questData[quest_obj][2][opt]);

                            survey_quest['questions'] = create_perc_quest(text, quest_id, question_opt, 5);
                        }
                        else if(questData[quest_obj][obj].type === 'AGR5'){
                            question_opt = [];
                            for(opt in questData[quest_obj][2])
                                question_opt.push(questData[quest_obj][2][opt]);

                            survey_quest['questions'] = create_perc_quest(text, quest_id, question_opt, 5);
                        }
                        else{           //case for custom options
                            question_opt = [];
                            for(opt in questData[quest_obj][2])
                                question_opt.push(questData[quest_obj][2][opt]);

                            if(questData[quest_obj][1].takes_multiple === 'true')
                                survey_quest['questions'] = create_multiple_opt_quest(text, quest_id, question_opt, 5);
                            else
                                survey_quest['questions'] = create_perc_quest(text, quest_id, question_opt, 5);
                        }

                        questions.push(survey_quest);
                    }
                }
            }
        }
        return questions;
    }

     //basic json object for survey creation
     var surveyjson = {
          title: questData.title,
          showProgressBar: "bottom",
          firstPageIsStarted: true,
          startSurveyText: "Start",
     };

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

    //inserting all questions of questionnaire in survey
    surveyjson['pages'] = create_questions_list();
    let survey_results = {};
    console.log(surveyjson);
    window.survey = new Survey.Model(surveyjson);
    survey
        .onComplete
        .add(function (result) {
            survey_results['data'] = JSON.stringify(result.data);
            console.log(survey_results);
            $('.row-compl').show();
            survey_results['ass_id'] = ass_id;
            var csrftoken = getCookie('csrftoken');
            $.ajax({
                type: "POST",
                headers: { "X-CSRFToken": csrftoken },
                dataType: 'json',
                url: '/survey_submit/',
                data: survey_results,
                success: function(result){
                    if(result['result'] === 'Success') {
                        console.log(result);
                    }
                }
            })
        });

    $("#surveyElement").Survey({model: survey});

});