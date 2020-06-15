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

    console.log(assignment_info);

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

    function create_survey_description(assignment_info){
        return 'Campign title: ' +assignment_info['campaign_title']+'\n'+
            'Domain: '+assignment_info['domain']+'\n'+
            'Dimension: '+assignment_info['dimension']+'\n' +
            'Descrption: '+assignment_info['domain_descr']
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
    console.log(survey);

    // This event is fired up when the survey is rendered and hides the SurveyJS built in title and shows a custom jumbotron about survey info
    survey.onAfterRenderSurvey.add(function () {
        $('.sv-title').hide();

        let jumbotron = '<div data-bind="css: css.header" class="sv-title sv-container-modern__title" style="">'
        +'<div class="row">'
        +    '<div class="jumbotron infos" style="font-weight: 400; color: #dae1e7 !important; '
        +            'background-color: #004895; padding: 1.5rem 1.5rem; margin-bottom: 0; width: 100%">'
        +        '<div class="row" style="margin-bottom: 1%;">'
        +            '<h2 class="display-4">'+quest_title+'</h2>'
        +        '</div>';

        let campaign_info ='<div class="row" style="margin-bottom: 1%;">'
        +            '<div class="col-md-2">'
        +                'Campaign: '
        +            '</div>'
        +            '<div class="col-md-10" style="font-weight: 500;">'
        +                assignment_info.campaign_title
        +             '</div>'
        +        '</div>';

        let quest_info = '<div class="row" style="margin-bottom: 1%;">'
        +            '<div class="col-md-2">'
        +                'Dimension: '
        +            '</div>'
        +            '<div class="col-md-10" style="font-weight: 500;">'
        +                assignment_info.dimension
        +            '</div>'
        +        '</div>'
        +        '<div class="row" style="margin-bottom: 1%;">'
        +            '<div class="col-md-2">'
        +                'Domain: '
        +            '</div>'
        +            '<div class="col-md-10" style="font-weight: 500;">'
        +                assignment_info.domain
        +            '</div>'
        +        '</div>'
        +        '<hr class="my-4">'
        +        '<h4>Description</h4>'
        +        '<p style="font-weight: 400;">'+assignment_info.domain_descr+'</p> '
        +    '</div>'
        +'</div>'
        +'</div>';

        jumbotron = (is_assignment === 'true') ? jumbotron + campaign_info + quest_info : jumbotron + quest_info

        $('.sv-container-modern').prepend(jumbotron)
    })


    //When the survey starts the infos jumbotron is hidden and the default title is shown
    survey.onStarted.add(function () {
        $('.infos').hide();
        $('.sv-title').show();
    })

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