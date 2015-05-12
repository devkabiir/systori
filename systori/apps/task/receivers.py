from django.db.models.signals import pre_delete, m2m_changed
from django_fsm.signals import post_transition
from django.dispatch import receiver
from ..document.models import Proposal
from ..task.models import Job


@receiver(m2m_changed, sender=Proposal.jobs.through)
def proposal_create_handler(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for job in Job.objects.filter(id__in=pk_set).all():
            job.propose()
            job.save()


@receiver(post_transition, sender=Proposal)
def proposal_transition_handler(sender, instance, name, source, target, **kwargs):

    for job in instance.jobs.all():

        if target == instance.APPROVED:
            job.approve()
            job.save()

        elif target == instance.DECLINED:
            job.draft()
            job.save()


@receiver(pre_delete, sender=Proposal)
def proposal_delete_handler(sender, instance, **kwargs):
    for job in instance.jobs.all():
        job.draft()
        job.save()