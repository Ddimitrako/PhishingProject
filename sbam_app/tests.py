from django.test import TestCase

from sbam_app import models
from sbam_app import views


def assignWeights(questions, weights):
    i = 0
    for question in questions:
        question.weight = weights[i]
        question.save()
        # print('%s%s%s' % (question.id, ' was assigned ', question.weight))
        i += 1


class CalculateAssignmentResultsTestCase(TestCase):
    fixtures = ['security_culture_model.json', 'test_calculate_results.json']

    def testNoWeightsUnitarySameType(self):
        # Questionnaires contain questions that bear the same unitary scale (values varying from 0 to 1) and
        # are of the same question type.
        # Additionally, all question weights are set equal to 1 (in other words, weight is not being used)
        #
        # Answers (QuestionType): question_option(=value)

        # Answers (AGR5): 35(=0), 39(=1), 36(=0.25), 43(=0.25)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=1)).score,
                         0.375)

        # Answers (AGR5): 36(=0.25), 42(=0.5), 37(=0.5), 36(=0.25)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=2)).score,
                         0.375)

        # Answers (AGR5): 36(=0.25), 43(=0.25), 39(=1), 35(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=3)).score,
                         0.375)

        # Answers (AGR5): 41(=0.75), 37(=0.5), 35(=0), 39(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=4)).score,
                         0.5625)

    def testNoWeightsScaled(self):
        # Questionnaires contain questions that bear the same scale (values varying from 1 to 4).
        # Additionally, all question weights are set equal to 1 (in other words, weight is not being used)
        #
        # Answers (QuestionType): question_option(=value)

        # Answers (CUSTOM): 10015(=2), 10001(=4), 10008(=1), 10010(=3), 10017(=4)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=5)).score,
                         0.7)

        # Answers (CUSTOM): 10019(=2), 10001(=4), 10005(=4), 10012(=1), 10015(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=6)).score,
                         0.65)

        # Answers (CUSTOM): 10016(=1), 10012(=1), 10008(=1), 10004(=1), 10020(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=7)).score,
                         0.25)

        # Answers (CUSTOM): 10001(=4), 10012(=1), 10014(=3), 10018(=3), 10007(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=8)).score,
                         0.65)

    def testNoWeightsUnitaryVariousTypes(self):
        # Questionnaires contain questions that bear the same unitary scale (values varying from 0 to 1)
        # but have various question types.
        # Additionally, all question weights are set equal to 1 (in other words, weight is not being used)
        #
        # Answers (QuestionType): question_option(=value)

        # Answers (BOOL & PERC10): 2(=0), 2(=0), 1(=1), 1(=1), 2(=0), 23(=0.11), 1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=9)).score,
                         0.4442857142857143)

        # Answers (BOOL & PERC10): 1(=1), 1(=1), 1(=1), 2(=0), 1(=1), 17(=0.77), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=10)).score,
                         0.6814285714285714)

        # Answers (BOOL & PERC10): 1(=1), 1(=1), 1(=1), 1(=1), 1(=1), 19(=0.55), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=11)).score,
                         0.7928571428571428)

        # Answers (BOOL & PERC10): 2(=0), 1(=1), 1(=1), 2(=0), 1(=1), 21(=0.33), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=12)).score,
                         0.4757142857142857)

    def testWithWeightsUnitarySameType(self):
        # Questionnaires contain questions that bear the same unitary scale (values varying from 0 to 1) and
        # are of the same question type.
        # Additionally, each question is assigned a specific weight
        #
        # Answers (QuestionType): question_id(=weight)-question_option(=value)
        weights = [2, 1, 3, 4]  # total = 10
        questions = models.Question.objects.filter(is_active=True, id__in=[10011, 10012, 10014, 10015]).order_by('id')
        assignWeights(questions, weights)

        # Answers (AGR5): 10011(=2)-35(=0), 10012(=1)-39(=1), 10014(=3)-36(=0.25), 10015(=4)-43(=0.25)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=1)).score,
                         0.275)

        # Answers (AGR5): 10011(=2)-36(=0.25), 10015(=4)-42(=0.5), 10014(=3)-37(=0.5), 10012(=1)-36(=0.25)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=2)).score,
                         0.425)

        # Answers (AGR5): 10011(=2)-36(=0.25), 10015(=4)-43(=0.25), 10014(=3)-39(=1), 10012(=1)-35(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=3)).score,
                         0.45)

        # Answers (AGR5): 10015(=4)-41(=0.75), 10012(=1)-37(=0.5), 10014(=3)-35(=0), 10011(=2)-39(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=4)).score,
                         0.55)

    def testWithWeightsScaled(self):
        # Questionnaires contain questions that bear the same scale (values varying from 1 to 4).
        # Additionally, each question is assigned a specific weight
        #
        # Answers (QuestionType): question_id(=weight)-question_option(=value)

        weights = [15, 35, 10, 15, 5]  # Total = 80
        questions = models.Question.objects.filter(is_active=True,
                                                   id__in=[10016, 10017, 10018, 10019, 10020]). \
            order_by('id')
        assignWeights(questions, weights)

        # Answers (CUSTOM): 10019(=15)-10015(=2), 10016(=15)-10001(=4), 10017(=35)-10008(=1),
        #                   10018(=10)-10010(=3), 10020(=5)-10017(=4)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=5)).score,
                         0.546875)

        # Answers (CUSTOM): 10020(=5)-10019(=2), 10016(=15)-10001(=4), 10017(=35)-10005(=4),
        #                   10018(=10)-10012(=1), 10019(=15)-10015(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=6)).score,
                         0.78125)

        # Answers (CUSTOM): 10019(=15)-10016(=1), 10018(=10)-10012(=1), 10017(=35)-10008(=1),
        #                   10016(=15)-10004(=1), 10020(=5)-10020(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=7)).score,
                         0.25)

        # Answers (CUSTOM): 10016(=15)-10001(=4), 10018(=10)-10012(=1), 10019(=15)-10014(=3),
        #                   10020(=5)-10018(=3), 10017(=35)-10007(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=8)).score,
                         0.625)

    def testWithWeightsUnitaryVariousTypes(self):
        # Questionnaires contain questions that bear the same unitary scale (values varying from 0 to 1)
        # but have various question types.
        # Additionally, each question is assigned a specific weight
        #
        # Answers (QuestionType): question_id(=weight)-question_option(=value)

        weights = [5, 20, 5, 40, 7.5, 10, 12.5]  # Total = 100
        questions = models.Question.objects.filter(is_active=True,
                                                   id__in=[10001, 10002, 10003, 10004, 10005, 10008, 10010]). \
            order_by('id')
        assignWeights(questions, weights)

        # Answers (BOOL & PERC10): 10004(=40)-2(=0), 10002(=20)-2(=0), 10005(=7.5)-1(=1), 10003(=5)-1(=1),
        #                          10010(=12.5)-2(=0), 10008(=10)-23(=0.11), 10001(=5)-1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=9)).score,
                         0.18600000000000003)

        # Answers (BOOL & PERC10): 10001(=5)-1(=1), 10002(=20)-1(=1), 10003(=5)-1(=1), 10004(=40)-2(=0),
        #                          10005(=7.5)-1(=1), 10008(=10)-17(=0.77), 10010(=12.5)-2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=10)).score,
                         0.452)

        # Answers (BOOL & PERC10): 10001(=5)-1(=1), 10010(=12.5)-2(=0), 10008(=10)-19(=0.55), 10005(=7.5)-1(=1),
        #                          10004(=40)-1(=1), 10003(=5)-1(=1), 10002(=20)-1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=11)).score,
                         0.83)

        # Answers (BOOL & PERC10): 10001(=5)-2(=0), 10003(=5)-1(=1), 10004(=40)-1(=1), 10005(=7.5)-2(=0),
        #                          10008(=10)-21(=0.33), 10010(=12.5)-1(=1), 10002(=20)-2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=12)).score,
                         0.608)
