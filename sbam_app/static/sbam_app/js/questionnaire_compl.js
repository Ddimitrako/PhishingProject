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
    function create_bool_quest(text, quest_id, question_opt){
        question_obj = {};
        question_obj = {
            type: "boolean",
            name: "question_"+quest_id,
            title: 'Please answer the question',
            label: text,
            labelTrue: question_opt[0].text,
            labelFalse: question_opt[1].text,
            isRequired: true,
            valueTrue: question_opt[0].id,
            valueFalse: question_opt[1].id
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
            survey_quest = {};
            question_opt = [];

            for(opt in questData[quest_obj]['question_options'])
                question_opt.push(questData[quest_obj]['question_options'][opt]);

            if(questData[quest_obj]['question_type'].type.startsWith('BOOL'))
                survey_quest['questions'] = create_bool_quest(questData[quest_obj]['question'].text, questData[quest_obj]['question'].id, question_opt);
            else if(questData[quest_obj]['question_type'].takes_multiple === 'true')
                survey_quest['questions'] = create_multiple_opt_quest(questData[quest_obj]['question'].text, questData[quest_obj]['question'].id, question_opt, 5);
            else
                survey_quest['questions'] = create_perc_quest(questData[quest_obj]['question'].text, questData[quest_obj]['question'].id, question_opt, 5);

            questions.push(survey_quest);
        }
        return questions;
    }

     //basic json object for survey creation
     console.log(current_lang);
     var surveyjson = {
          title: quest_title,
          locale: current_lang,
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
            if (is_assignment === 'true') {
                $.ajax({
                    type: "POST",
                    headers: {"X-CSRFToken": csrftoken},
                    dataType: 'json',
                    url: '/survey_submit/',
                    data: survey_results,
                    success: function (result) {
                        if (result['result'] === 'success') {
                            $('.badge').addClass(result['badge']);
                            $('.badge').text(result['score']);
                            $('#selfAssessmentCompletion').modal('toggle')
                        }
                    }
                })
            }
            else{

                $.ajax({
                    type: "POST",
                    headers: {"X-CSRFToken": csrftoken},
                    dataType: 'json',
                    url: '/self_assessment_submit/',
                    data: survey_results,
                    success: function (result) {
                        if (result['result'] === 'success') {
                            $('.badge').addClass(result['badge']);
                            $('.badge').text(result['score']);
                            $('#selfAssessmentCompletion').modal('toggle')
                        }
                    }
                })
            }
        });

    $("#surveyElement").Survey({model: survey});

});