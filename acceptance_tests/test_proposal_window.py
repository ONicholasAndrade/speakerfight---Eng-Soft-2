from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils.timezone import now

from model_mommy import mommy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from deck.models import Event, Proposal


class ProposalWindowAcceptanceTests(StaticLiveServerTestCase):

    def setUp(self):

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.browser = webdriver.Chrome(
            options=options
        )

        self.user = User.objects.create_user(
            username='thiago',
            password='123456'
        )


    def tearDown(self):
        self.browser.quit()


    def login(self):

        self.browser.get(
            self.live_server_url +
            '/accounts/login/'
        )

        self.browser.find_element(
            By.NAME,
            'login'
        ).send_keys(
            'thiago'
        )

        self.browser.find_element(
            By.NAME,
            'password'
        ).send_keys(
            '123456'
        )

        self.browser.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]'
        ).click()


    def test_before_opening_date_blocks_access(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() + timedelta(days=2),
            closing_date=now() + timedelta(days=5)
        )

        self.login()

        self.browser.get(
            self.live_server_url +
            '/events/{}/proposals/create/'.format(event.slug)
        )

        self.assertIn(
            "This Event doesn't accept Proposals yet.",
            self.browser.page_source
        )


    def test_create_proposal_after_opening_date(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=1),
            closing_date=now() + timedelta(days=5)
        )

        self.login()

        self.browser.get(
            self.live_server_url +
            '/events/{}/proposals/create/'.format(event.slug)
        )


        self.browser.find_element(
            By.NAME,
            'title'
        ).send_keys(
            'Proposta Selenium'
        )


        self.browser.find_element(
            By.NAME,
            'description'
        ).send_keys(
            'Descricao criada pelo teste de aceitacao'
        )


        self.browser.find_element(
            By.CSS_SELECTOR,
            'button[type="submit"]'
        ).click()


        self.assertIn(
            'Proposal created.',
            self.browser.page_source
        )


        self.assertEqual(
            Proposal.objects.count(),
            1
        )


    def test_after_closing_date_blocks_access(self):

        event = mommy.make(
            Event,
            accept_proposals_at=now() - timedelta(days=5),
            closing_date=now() - timedelta(days=1)
        )

        self.login()

        self.browser.get(
            self.live_server_url +
            '/events/{}/proposals/create/'.format(event.slug)
        )

        self.assertIn(
            "This Event doesn't accept Proposals anymore.",
            self.browser.page_source
        )