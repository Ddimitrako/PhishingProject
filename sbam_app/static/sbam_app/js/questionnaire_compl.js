$(document).ready(function(){
     // console.log(questData);
    // Survey
    // .StylesManager
    // .applyTheme("bootstrap");


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


    //Gathers all questions of survey and creates appropriate json object for each question
    function create_questions_list(){
        questions = [];
        question_obj = {};
        start = [{
            type: "html",
            html: "You are about to start quiz by history. <br/>" +
            "You have 10 seconds for every page and 25 seconds for the whole survey of 3 questions.<br/>" +
            "Please click on <b>'Start Quiz'</b> " +
            "button when you are ready."
        }];

        question_obj['questions'] = start;
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
                        switch (questData[quest_obj][obj].type) {
                            case 'BL':
                                question_opt_ids = [];
                                for(opt in questData[quest_obj][2]){

                                    // console.log(opt, questData[quest_obj][2][opt]);
                                    question_opt_ids.push(questData[quest_obj][2][opt].id);
                                }
                                console.log('Edwwww', question_opt_ids);

                                bool_obj = {};
                                bool_obj['questions'] = create_bool_quest(text, quest_id, question_opt_ids);
                                questions.push(bool_obj);
                                break;
                            case 'AG':
                                break;
                            default:

                        }

                        // if(questData[quest_obj][obj].type === 'BL') {
                        //     bool_obj = {};
                        //     bool_obj['questions'] = create_bool_quest(text, quest_id);
                        //     questions.push(bool_obj);
                        // }
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
          startSurveyText: "Start Quiz",
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
             // document
             //     .querySelector('#surveyResult').innerHTML = '' +
                 // '<div class="row>" ' +
                 // '<a class="btn btn-primary" href="{% url \'sbam:dashboard\' %}" role="button">{% trans "Start!" %}</a>' +
                 // '';
                 // .textContent = "Result JSON:\n" + JSON.stringify(result.data, null, 3);
             survey_results['data'] = JSON.stringify(result.data);
             console.log(survey_results);

                $('.row-compl').show();
         });

     $("#surveyElement").Survey({model: survey});
     // console.log(survey_results);
    $('.btn-compl').click(function () {
        // alert(survey_results);
        survey_results['ass_id'] = ass_id;
        var csrftoken = getCookie('csrftoken');
        $.ajax({
                type: "POST",
                headers: { "X-CSRFToken": csrftoken },
                dataType: 'json',
                url: '/sbam/survey_submit/',
                data: survey_results,
                success: function(result){

                    if(result['result'] === 'Success') {
                        alert('Ola good');
                        console.log(result);
                    }
                }
            })
    });
});