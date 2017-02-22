from django.urls import reverse

from systori.lib.testing import ClientTestCase

from ..document.factories import ProposalFactory, LetterheadFactory
from ..task.factories import JobFactory
from ..task.models import Job

from .factories import ProjectFactory, JobSiteFactory
from .models import Project, JobSite


class TestProjectListView(ClientTestCase):

    def test_load_without_search_term(self):
        response = self.client.get(reverse('projects'))
        self.assertEqual(200, response.status_code)

    def test_load_expected_variables(self):
        ProjectFactory()
        response = self.client.get(reverse('projects'))
        for element in ['sys-sort-button', 'sys-phase-button', 'sys-project-tile']:
            self.assertContains(response, element)
        for phase in dict(Project.PHASE_CHOICES).keys():
            self.assertContains(response, phase)


class TestProgressViews(ClientTestCase):

    def test_project_progress(self):
        project = ProjectFactory()
        response = self.client.get(reverse('project.progress', args=[project.id]), {})
        self.assertEqual(200, response.status_code)

    def test_project_progress_all(self):
        response = self.client.get(reverse('project.progress.all'), {})
        self.assertEqual(200, response.status_code)


class TestProjectTemplateViews(ClientTestCase):

    def test_view_templates(self):
        response = self.client.get(reverse('templates'), {})
        self.assertEqual(200, response.status_code)


class TestProjectViews(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.data = {
            'name': 'new test project',
            'structure': '0.0',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
        }

    def test_create_project_initial(self):
        response = self.client.get(reverse('project.create'))
        self.assertEqual(200, response.status_code)

    def test_create_project_invalid(self):
        self.data['name'] = ''
        response = self.client.post(reverse('project.create'), self.data)
        self.assertEqual(200, response.status_code)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.']
        })

    def test_create_project_success_with_jobsite(self):
        response = self.client.post(reverse('project.create'), self.data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('projects'))
        self.assertTrue(Project.objects.filter(name='new test project').exists())
        self.assertEqual(1, Job.objects.count())
        self.assertEqual(1, JobSite.objects.count())
        self.assertEqual(self.data['address'], JobSite.objects.get().address)

    def test_create_project_success_without_jobsite(self):
        self.company.is_jobsite_required = False
        self.company.save()
        response = self.client.post(reverse('project.create'), self.data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(Project.objects.filter(name='new test project').exists())
        self.assertEqual(1, Job.objects.count())
        self.assertEqual(0, JobSite.objects.count())

    def test_create_project_success_with_goto_project(self):
        self.data['save_goto_project'] = ''
        response = self.client.post(reverse('project.create'), self.data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[2]))

    def test_update_project_initial(self):
        project = ProjectFactory(with_job=True)
        response = self.client.get(reverse('project.edit', args=[project.pk]))
        self.assertEqual(200, response.status_code)
        self.assertEqual('01.01.001', str(response.context['form'].initial['structure']))

    def test_update_project_success(self):
        data = {
            'name': 'updated project',
            'structure': '0.0.0'
        }
        project = ProjectFactory(with_job=True)
        response = self.client.post(reverse('project.edit', args=[project.pk]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('projects'))
        self.assertEqual('01.01.001', project.structure.pattern)
        project.refresh_from_db()
        self.assertEqual('0.0.0', project.structure.pattern)

    def test_update_project_invalid(self):
        data = {
            'name': 'updated project',
            'structure': '0.0.0.0'
        }
        project = ProjectFactory(with_job=True)
        response = self.client.post(reverse('project.edit', args=[project.pk]), data)
        self.assertEqual(200, response.status_code)
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'structure': ['Cannot change depth after project has been created.']
        })

    def test_update_project_success_with_goto_project(self):
        data = {
            'name': 'updated project',
            'structure': '0.0.0',
            'save_goto_project': ''
        }
        project = ProjectFactory(with_job=True)
        response = self.client.post(reverse('project.edit', args=[project.pk]), data)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, reverse('project.view', args=[2]))

    def test_view_project(self):
        project = ProjectFactory()
        job = JobFactory(project=project)
        proposal = ProposalFactory(
            project=project,
            letterhead=LetterheadFactory(),
        )
        proposal.jobs.add(job)
        response = self.client.get(reverse('project.view', args=[project.pk]), {})
        self.assertEqual(200, response.status_code)

    def test_phase_transition(self):
        project = ProjectFactory()
        self.assertEqual(project.phase, Project.PROSPECTIVE)
        for action, phase in [('begin_tendering', Project.TENDERING), ('begin_planning', Project.PLANNING)]:
            response = self.client.get(
                reverse('project.transition.phase', args=[project.pk, action])
            )
            self.assertEqual(response.status_code, 302)
            project.refresh_from_db()
            self.assertEqual(project.phase, phase)

    def test_phase_invalid_action_does_nothing(self):
        project = ProjectFactory()
        self.assertEqual(project.phase, Project.PROSPECTIVE)
        response = self.client.get(
            reverse('project.transition.phase', args=[project.pk, 'invalid'])
        )
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.phase, Project.PROSPECTIVE)

    def test_state_transition(self):
        project = ProjectFactory()
        self.assertEqual(project.state, Project.ACTIVE)
        for action, state in [('pause', Project.PAUSED), ('stop', Project.STOPPED)]:
            response = self.client.get(
                reverse('project.transition.state', args=[project.pk, action])
            )
            self.assertEqual(response.status_code, 302)
            project.refresh_from_db()
            self.assertEqual(project.state, state)

    def test_state_invalid_action_does_nothing(self):
        project = ProjectFactory()
        self.assertEqual(project.state, Project.ACTIVE)
        response = self.client.get(
            reverse('project.transition.state', args=[project.pk, 'invalid'])
        )
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.state, Project.ACTIVE)


class TestJobSiteViews(ClientTestCase):

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_create_jobsite_initial_without_previous(self):
        response = self.client.get(reverse('jobsite.create', args=[self.project.pk]))
        self.assertEqual(200, response.status_code)
        initial = response.context['form'].initial
        self.assertEqual(initial['name'], '')
        self.assertEqual(initial['address'], '')
        self.assertEqual(initial['city'], '')
        self.assertEqual(initial['postal_code'], '')

    def test_create_jobsite_initial_with_previous(self):
        jobsite = JobSiteFactory(project=self.project)
        response = self.client.get(reverse('jobsite.create', args=[self.project.pk]))
        self.assertEqual(200, response.status_code)
        initial = response.context['form'].initial
        self.assertEqual(initial['name'], '')
        self.assertEqual(initial['address'], jobsite.address)
        self.assertEqual(initial['city'], jobsite.city)
        self.assertEqual(initial['postal_code'], jobsite.postal_code)

    def test_create_jobsite_invalid(self):
        data = {
            'name': '',
            'address': '',
            'city': '',
            'postal_code': '',
        }
        response = self.client.post(reverse('jobsite.create', args=[self.project.pk]), data)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(0, JobSite.objects.count())

    def test_create_jobsite_success(self):
        data = {
            'name': '1st floor',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
        }
        self.assertEqual(0, JobSite.objects.count())
        response = self.client.post(reverse('jobsite.create', args=[self.project.pk]), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(JobSite.objects.filter(name='1st floor').exists())

    def test_update_jobsite_initial(self):
        jobsite = JobSiteFactory(project=self.project)
        response = self.client.get(reverse('jobsite.edit', args=[self.project.pk, jobsite.pk]))
        self.assertEqual(200, response.status_code)

    def test_update_jobsite_success(self):
        jobsite = JobSiteFactory(project=self.project)
        data = {
            'name': '1st floor',
            'address': 'One Street',
            'city': 'Town',
            'postal_code': '12345',
        }
        response = self.client.post(reverse('jobsite.edit', args=[self.project.pk, jobsite.pk]), data)
        self.assertEqual(302, response.status_code)
        jobsite.refresh_from_db()
        self.assertEqual(data['name'], jobsite.name)
        self.assertEqual(data['address'], jobsite.address)

    def test_delete_jobsite(self):
        jobsite = JobSiteFactory(project=self.project)
        self.assertEqual(1, JobSite.objects.count())
        response = self.client.get(reverse('jobsite.delete', args=[self.project.pk, jobsite.pk]))
        self.assertEqual(200, response.status_code)
        response = self.client.post(reverse('jobsite.delete', args=[self.project.pk, jobsite.pk]))
        self.assertEqual(302, response.status_code)
        self.assertEqual(0, JobSite.objects.count())
