from django.conf.urls import url
from ..user.authorization import office_auth
from ..accounting.views import PaymentCreate, PaymentDelete
from .views import *
from ..task.views import AllProjectsProgress

urlpatterns = [

    url(r'^projects/(?P<phase_filter>\w+)?$', office_auth(ProjectList.as_view()), name='projects'),
    url(r'^create-project$', office_auth(ProjectCreate.as_view()), name='project.create'),
    url(r'^import-project$', office_auth(ProjectImport.as_view()), name='project.import'),
    url(r'^project-(?P<pk>\d+)$', office_auth(ProjectView.as_view()), name='project.view'),
    url(r'^project-(?P<pk>\d+)/edit$', office_auth(ProjectUpdate.as_view()), name='project.edit'),
    url(r'^project-(?P<pk>\d+)/plan$', office_auth(ProjectPlanning.as_view()), name='project.plan'),
    url(r'^project-(?P<pk>\d+)/delete$', office_auth(ProjectDelete.as_view()), name='project.delete'),
    url(r'^project-(?P<pk>\d+)/transition/phase/(?P<transition>\w+)$', office_auth(ProjectManualPhaseTransition.as_view()), name='project.transition.phase'),
    url(r'^project-(?P<pk>\d+)/transition/state/(?P<transition>\w+)$', office_auth(ProjectManualStateTransition.as_view()), name='project.transition.state'),
    url(r'^templates$', office_auth(TemplatesView.as_view()), name='templates'),

    url(r'^project-(?P<project_pk>\d+)/create-jobsite$', office_auth(JobSiteCreate.as_view()), name='jobsite.create'),
    url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/edit$', office_auth(JobSiteUpdate.as_view()), name='jobsite.edit'),
    url(r'^project-(?P<project_pk>\d+)/jobsite-(?P<pk>\d+)/delete$', office_auth(JobSiteDelete.as_view()), name='jobsite.delete'),

    url(r'^project-(?P<pk>\d+)/progress', office_auth(ProjectProgress.as_view()), name='project.progress'),
    url(r'^progress$', office_auth(AllProjectsProgress.as_view()), name='project.progress.all'),
]
