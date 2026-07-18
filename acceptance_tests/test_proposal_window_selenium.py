# -*- coding: utf-8 -*-

import os
import time
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from django.test import override_settings
from django.utils.timezone import now

from model_mommy import mommy
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from deck.models import Event, Proposal


@override_settings(
    ALLOWED_HOSTS=['localhost', '127.0.0.1', 'web'],
    SEND_NOTIFICATIONS=False,
)
class ProposalWindowSeleniumTests(StaticLiveServerTestCase):
    """Testes funcionais da janela de propostas em um navegador real."""

    host = '0.0.0.0'
    port = 8081
    timeout = 10

    @classmethod
    def setUpClass(cls):
        super(ProposalWindowSeleniumTests, cls).setUpClass()

        cls.browser_base_url = os.environ.get(
            'SELENIUM_BROWSER_URL',
            cls.live_server_url.replace('0.0.0.0', '127.0.0.1')
        )

        cls.selenium = cls._create_remote_browser()
        cls.selenium.implicitly_wait(2)
        cls.selenium.set_window_size(1280, 1024)

    @classmethod
    def tearDownClass(cls):
        try:
            if getattr(cls, 'selenium', None):
                cls.selenium.quit()
        finally:
            super(ProposalWindowSeleniumTests, cls).tearDownClass()

    @classmethod
    def _create_remote_browser(cls):
        selenium_url = os.environ.get(
            'SELENIUM_URL',
            'http://selenium:4444/wd/hub'
        )

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1280,1024')

        last_error = None

        # O container do Selenium pode estar iniciado, mas o Grid ainda
        # pode precisar de alguns segundos para aceitar uma sessão.
        for attempt in range(30):
            try:
                return webdriver.Remote(
                    command_executor=selenium_url,
                    desired_capabilities=options.to_capabilities(),
                )
            except WebDriverException as error:
                last_error = error
                time.sleep(2)

        raise last_error

    def setUp(self):
        self.selenium.delete_all_cookies()

        self.user = User.objects.create_user(
            username='usuario_selenium',
            email='selenium@example.com',
            password='123456',
        )

        # O login é preparado pelo Django e a sessão é transferida para o
        # navegador. O fluxo da janela de propostas é executado pelo Selenium.
        self.client.force_login(self.user)
        self._authenticate_browser_with_django_session()

    def _authenticate_browser_with_django_session(self):
        self.selenium.get(self.browser_base_url + '/')
        self._wait_for_body()

        session_cookie = self.client.cookies[settings.SESSION_COOKIE_NAME]
        self.selenium.add_cookie({
            'name': settings.SESSION_COOKIE_NAME,
            'value': session_cookie.value,
            'path': '/',
        })

    def _create_event(self, accept_proposals_at, closing_date):
        return mommy.make(
            Event,
            author=self.user,
            title='Evento de teste Selenium',
            accept_proposals_at=accept_proposals_at,
            closing_date=closing_date,
        )

    def _proposal_url(self, event):
        return self.browser_base_url + reverse(
            'create_event_proposal',
            args=[event.slug],
        )

    def _wait_for_body(self):
        return WebDriverWait(self.selenium, self.timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

    def _wait_for_event_page(self, event):
        WebDriverWait(self.selenium, self.timeout).until(
            lambda browser: event.get_absolute_url() in browser.current_url
        )
        return self._wait_for_body()

    def test_browser_blocks_proposal_before_opening_date(self):
        event = self._create_event(
            accept_proposals_at=now() + timedelta(days=2),
            closing_date=now() + timedelta(days=5),
        )

        self.selenium.get(self._proposal_url(event))
        body = self._wait_for_event_page(event)

        self.assertIn(
            "This Event doesn't accept Proposals yet.",
            body.text,
        )
        self.assertEqual(Proposal.objects.count(), 0)

    def test_browser_creates_proposal_during_valid_period(self):
        event = self._create_event(
            accept_proposals_at=now() - timedelta(days=1),
            closing_date=now() + timedelta(days=5),
        )

        proposal_title = 'Proposta criada pelo Selenium'
        description_text = (
            'Descricao preenchida por um navegador controlado pelo Selenium.'
        )

        self.selenium.get(self._proposal_url(event))

        title = WebDriverWait(self.selenium, self.timeout).until(
            EC.element_to_be_clickable((By.ID, 'id_title'))
        )

        title.clear()
        title.send_keys(proposal_title)

        WebDriverWait(self.selenium, self.timeout).until(
            lambda browser: browser.execute_script(
                """
                return typeof window.tinymce !== 'undefined'
                    && window.tinymce.get('id_description') !== null;
                """
            )
        )

        self.selenium.execute_script(
            """
            var editor = window.tinymce.get('id_description');
            editor.setContent(arguments[0]);
            editor.save();
            window.tinymce.triggerSave();
            """,
            description_text,
        )

        description = self.selenium.find_element_by_id('id_description')

        self.assertIn(
            description_text,
            description.get_attribute('value'),
        )

        proposal_form = title.find_element_by_xpath('./ancestor::form[1]')

        submit_buttons = proposal_form.find_elements_by_css_selector(
            'button[type="submit"], input[type="submit"]'
        )

        self.assertTrue(
            submit_buttons,
            'Nenhum botao de envio foi encontrado no formulario.'
        )

        submit_button = submit_buttons[0]

        self.selenium.execute_script(
            'arguments[0].scrollIntoView(true);',
            submit_button,
        )

        submit_button.click()

        body = self._wait_for_event_page(event)

        self.assertIn(proposal_title, body.text)
        self.assertTrue(
            Proposal.objects.filter(
                event=event,
                author=self.user,
                title=proposal_title,
            ).exists()
        )

    def test_browser_blocks_proposal_after_closing_date(self):
        event = self._create_event(
            accept_proposals_at=now() - timedelta(days=5),
            closing_date=now() - timedelta(days=1),
        )

        self.selenium.get(self._proposal_url(event))
        body = self._wait_for_event_page(event)

        self.assertIn(
            "This Event doesn't accept Proposals anymore.",
            body.text,
        )
        self.assertEqual(Proposal.objects.count(), 0)
