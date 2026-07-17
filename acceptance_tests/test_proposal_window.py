from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from model_mommy import mommy

from deck.models import Event, Proposal


class ProposalWindowAcceptanceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='thiago',
            password='123456'
        )

        self.client.login(
            username='thiago',
            password='123456'
        )


    def test_user_cannot_access_proposal_before_opening_date(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() + timedelta(days=2),
            closing_date=now() + timedelta(days=5)
        )

        response = self.client.get(
            reverse(
                'create_event_proposal',
                args=[event.slug]
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Proposal.objects.count(),
            0
        )


    def test_user_can_create_proposal_after_opening_date(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=1),
            closing_date=now() + timedelta(days=5)
        )

        response = self.client.get(
            reverse(
                'create_event_proposal',
                args=[event.slug]
            )
        )

        self.assertEqual(response.status_code, 200)


    def test_user_cannot_create_proposal_after_closing_date(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=5),
            closing_date=now() - timedelta(days=1)
        )

        response = self.client.get(
            reverse(
                'create_event_proposal',
                args=[event.slug]
            )
        )

        self.assertEqual(response.status_code, 302)