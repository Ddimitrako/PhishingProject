from django.urls import path

from sbam_app.views import *

app_name = 'sbam'

urlpatterns = [
    # Dashboard
    path('', dashboardView, name='dashboard'),

    # Self-Assessment
    path('selfassessment/', self_evaluation, name='self_assessment'),
    path('selfassessment/history', SelfEvaluationHistory.as_view(), name='self_assessment_history'),
    path('selfassessment/<quest_id>/', selfAssessmentCompletion, name='self_assessment_completion'),
    path('self_assessment_submit/', selfAssessmentSubmission, name='self_assessment_submit'),

    # Questionnaires
    path('questionnaires/', questionnaires_list, name='questionnaires_list'),
    path('questionnaires/<quest_id>/', questionnaireInfo, name='questionnaire_info'),

    # Assignments
    path('assignments/', AssignmentsHistory.as_view(), name='assignments_history'),
    path('assignments/<assignment_id>/', assignmentCompletion, name='assignments'),
    path('survey_submit/', surveySubmission, name='survey_submit'),

    # Users
    path('users/', UsersView.as_view(), name='users'),
    path('users/profile/<username>/', profile, name='profile'),
    path('users/profile/<username>/enable/', enable_user, name='enable_user'),
    path('users/profile/<username>/disable/', disable_user, name='disable_user'),
    path('users/create_user/', create_user, name='create_user'),

    # Groups
    path('groups/', GroupsView.as_view(), name='groups'),
    path('groups/group/<name>/', group, name='group'),
    path('groups/group/<name>/enable/', enable_group, name='enable_group'),
    path('groups/group/<name>/disable/', disable_group, name='disable_group'),
    path('groups/create_group/', create_group, name='create_group'),

    # Campaigns
    path('campaigns/', CampaignsView.as_view(), name='campaigns'),
    path('campaigns/campaign/<id>/', campaign, name='campaign'),
    path('campaigns/campaign/<id>/cancel/', cancel_campaign, name='cancel_campaign'),
    path('campaigns/create_campaign/', create_campaign, name='create_campaign'),
    path('campaigns/check_email/', check_email, name='check_email'),

    # Reports
    path('reports/', reports, name='reports'),
    path('get_reports_data/', get_reports_data, name='get_reports_data'),
    path('get_user_metrics/', get_user_metrics, name='get_user_metrics'),

    # Threats
    path('threats/', IdentifiedThreats, name='threats'),

    # results REST API
    path('api/token/',GetAccessToken.as_view(), name='get_token'),
    path('api/metrics/organization/', GetOrganizationReport.as_view(), name='organization_report'),
    path('api/metrics/campaigns/<campaign_id>/', GetCampaignReport.as_view(), name='campaign_report'),
    path('api/metrics/user/<user_id>/', GetUserReport.as_view(), name='user_report'),
    path('api/metrics/group/<group_id>/', GetGroupReport.as_view(), name='group_report'),
    path('api/metrics/campaigns/', GetCampaigns.as_view(), name='get_campaigns'),

    path('kafka/', CheckFinishedCampaigns, name='kafka')

]
