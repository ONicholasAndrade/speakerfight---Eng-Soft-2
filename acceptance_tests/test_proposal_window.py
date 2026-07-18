# -*- coding: utf-8 -*-

from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
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


    def test_before_opening_date_blocks_access(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() + timedelta(days=2),
            closing_date=now() + timedelta(days=5)
        )

        response = self.client.get(
            '/events/{}/proposals/create/'.format(event.slug)
        )

        self.assertEqual(
            response.status_code,
            302
        )


    def test_create_proposal_after_opening_date(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=1),
            closing_date=now() + timedelta(days=5)
        )

        proposal = mommy.make(
            Proposal,
            event=event,
            author=self.user,
            title='Proposta Selenium',
            description='Descricao criada pelo teste'
        )

        self.assertEqual(
            Proposal.objects.count(),
            1
        )

        self.assertEqual(
            proposal.event,
            event
        )


    def test_after_closing_date_blocks_access(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=5),
            closing_date=now() - timedelta(days=1)
        )

        response = self.client.get(
            '/events/{}/proposals/create/'.format(event.slug)
        )

        self.assertEqual(
            response.status_code,
            302
        )