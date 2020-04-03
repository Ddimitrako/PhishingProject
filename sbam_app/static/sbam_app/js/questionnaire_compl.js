$(document).ready(function(){
     console.log(questData);

    //  function responsible for creating boolean questions json for survey
    function create_bool_quest(text, quest_id){
        question_obj = {};
        question_obj = {
            type: "boolean",
            name: "question_"+quest_id,
            title: 'Please answer the question',
            label: text,
            isRequired: true

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
            console.log(quest_obj, questData[quest_obj]);
            if(quest_obj !== 'title') {
                for (let obj in questData[quest_obj]) {
                    var text;
                    var quest_id;

                    if (questData[quest_obj][obj].hasOwnProperty('text')) {
                        text = questData[quest_obj][obj].text;
                        quest_id = questData[quest_obj][obj].id;
                    }

                    if (questData[quest_obj][obj].hasOwnProperty('type')) {
                        if(questData[quest_obj][obj].type === 'BL') {
                            bool_obj = {};
                            bool_obj['questions'] = create_bool_quest(text, quest_id);
                            questions.push(bool_obj);
                        }

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

    //inserting all questions of questionnaire in survey
    surveyjson['pages'] = create_questions_list();

    console.log(surveyjson);
     window.survey = new Survey.Model(surveyjson);
     survey
         .onComplete
         .add(function (result) {
             document
                 .querySelector('#surveyResult')
                 .textContent = "Result JSON:\n" + JSON.stringify(result.data, null, 3);
         });

     $("#surveyElement").Survey({model: survey});
});