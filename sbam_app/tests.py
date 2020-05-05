from django.test import TestCase

from sbam_app import models
from sbam_app import views


class CalculateAssignmentResultsTestCase(TestCase):
    fixtures = ['security_culture_model.json', 'test_calculate_results.json']

    # All question weights are set equal to 1 (in other words, weight is not being used)
    def testNoWeights(self):
        # Answers (QuestionType): question_option(=value)

        # Answers (AGR5): 35(=1), 39(=5), 36(=2), 43(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=1)).score,
                         0.5)

        # Answers (AGR5): 36(=2), 42(=3), 37(=3), 36(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=2)).score,
                         0.5)

        # Answers (AGR5): 36(=2), 43(=2), 39(=5), 35(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=3)).score,
                         0.5)

        # Answers (AGR5): 41(=4), 37(=3), 35(=1), 39(=5)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=4)).score,
                         0.65)

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

        # Answers (BOOL & PERC10): 2(=0), 2(=0), 1(=1), 1(=1), 2(=0), 23(=0.2), 1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=9)).score,
                         0.4571428571428572)

        # Answers (BOOL & PERC10): 1(=1), 2(=0), 1(=1), 2(=0), 1(=1), 17(=0.8), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=10)).score,
                         0.6857142857142857)

        # Answers (BOOL & PERC10): 1(=1), 1(=1), 1(=1), 1(=1), 1(=1), 19(=0.6), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=11)).score,
                         0.7999999999999999)

        # Answers (BOOL & PERC10): 2(=0), 1(=1), 1(=1), 2(=0), 1(=1), 21(=0.4), 2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=12)).score,
                         0.4857142857142857)

    # Each question has been assigned a random weight:
    #
    # 10001(=0.8), 10002(=2), 10003(=5), 10004(=0.2), 10005(=1)
    # 10007(=4), 10008(=0.8), 10010(=2), 10011(=5), 10012(=0.2)
    # 10014(=1), 10015(=4), 10016(=0.8), 10017(=2), 10018(=5)
    # 10019(=0.2), 10020(=1)
    def testWithWeights(self, ):
        weights = [0.8, 2, 5, 0.2, 1, 4]
        questions = models.Question.objects.filter(is_active=True).order_by('id')

        i = 0
        for question in questions:
            question.weight = weights[i]
            question.save()
            # print('%s %s %s %s' % (question.id,'(=',question.weight,')'))
            i = (i + 1) if (i < len(weights) - 1) else 0

        # Answers (QuestionType): question_id(=weight)-question_option(=value)

        # Answers (AGR5): 10011(=5)-35(=1), 10012(=0.2)-39(=5), 10014(=1)-36(=2), 10015(=4)-43(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=1)).score,
                         0.3137254901960784)

        # Answers (AGR5): 10011(=5)-36(=2), 10015(=4)-42(=3), 10014(=1)-37(=3), 10012(=0.2)-36(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=2)).score,
                         0.49803921568627446)

        # Answers (AGR5): 10011(=5)-36(=2), 10015(=4)-43(=2), 10014(=1)-39(=5), 10012(=0.2)-35(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=3)).score,
                         0.4549019607843137)

        # Answers (AGR5): 10015(=4)-41(=4), 10012(=0.2)-37(=3), 10014(=1)-35(=1), 10011(=5)-39(=5)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=4)).score,
                         0.8352941176470589)

        # Answers (CUSTOM): 10019(=0.2)-10015(=2), 10016(=0.8)-10001(=4), 10017(=2)-10008(=1),
        #                   10018(=5)-10010(=3), 10020(=1)-10017(=4)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=5)).score,
                         0.6833333333333332)

        # Answers (CUSTOM): 10020(=1)-10019(=2), 10016(=0.8)-10001(=4), 10017(=2)-10005(=4),
        #                   10018(=5)-10012(=1), 10019(=0.2)-10015(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=6)).score,
                         0.5166666666666666)

        # Answers (CUSTOM): 10019(=0.2)-10016(=1), 10018(=5)-10012(=1), 10017(=2)-10008(=1),
        #                   10016(=0.8)-10004(=1), 10020(=1)-10020(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=7)).score,
                         0.25)

        # Answers (CUSTOM): 10016(=0.8)-10001(=4), 10018(=5)-10012(=1), 10019(=0.2)-10014(=3),
        #                   10020(=1)-10018(=3), 10017(=2)-10007(=2)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=8)).score,
                         0.4388888888888889)

        # Answers (BOOL & PERC10): 10004(=0.2)-2(=0), 10002(=2)-2(=0), 10005(=1)-1(=1), 10003(=5)-1(=1),
        #                          10010(=2)-2(=0), 10008(=0.8)-23(=0.2), 10001(=0.8)-1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=9)).score,
                         0.5898305084745762)

        # Answers (BOOL & PERC10): 10001(=0.8)-1(=1), 10002(=2)-1(=1), 10003(=5)-1(=1), 10004(=0.2)-2(=0),
        #                          10005(=1)-1(=1), 10008(=0.8)-17(=0.8), 10010(=2)-2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=10)).score,
                         0.8)

        # Answers (BOOL & PERC10): 10001(=0.8)-1(=1), 10010(=2)-2(=0), 10008(=0.8)-19(=0.6), 10005(=1)-1(=1),
        #                          10004(=0.2)-1(=1), 10003(=5)-1(=1), 10002(=2)-1(=1)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=11)).score,
                         0.8033898305084746)

        # Answers (BOOL & PERC10): 10001(=0.8)-2(=0), 10003(=5)-1(=1), 10004(=0.2)-1(=1), 10005(=1)-2(=0),
        #                          10008(=0.8)-21(=0.4), 10010(=2)-1(=1), 10002(=2)-2(=0)
        self.assertEqual(views.calculate_assignment_result(models.QuestionnaireAssignment.objects.get(pk=12)).score,
                         0.6372881355932204)
