# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils.timezone import now, timedelta

from deck.models import Event
from deck.tests.test_unit import EVENT_DATA


class ListEventsCharacterizationTests(TestCase):
    fixtures = ['user.json', 'socialapp.json']

    def setUp(self):
        self.client = Client()
        self.event_data = EVENT_DATA.copy()

    def create_published_event(self, title, **overrides):
        event_data = self.event_data.copy()
        event_data.update(
            title=title,
            is_published=True,
        )
        event_data.update(overrides)

        return Event.objects.create(**event_data)

    def create_sixteen_published_events(self):
        for index in xrange(16):
            self.create_published_event(
                title='Pagination Event {}'.format(index)
            )

    def test_search_event_by_description(self):
        self.create_published_event(
            title='Django Conference',
            description='Event about software architecture'
        )

        response = self.client.get(
            reverse('list_events'),
            data={'search': 'software architecture'}
        )

        self.assertEqual(200, response.status_code)
        self.assertQuerysetEqual(
            response.context['event_list'],
            ['<Event: Django Conference>']
        )

    def test_search_can_return_past_event_in_current_behavior(self):
        self.create_published_event(
            title='Legacy Conference',
            description='Historic Python event',
            closing_date=now() - timedelta(days=7)
        )

        response = self.client.get(
            reverse('list_events'),
            data={'search': 'Historic Python'}
        )

        self.assertEqual(200, response.status_code)
        self.assertQuerysetEqual(
            response.context['event_list'],
            ['<Event: Legacy Conference>']
        )

    def test_invalid_page_returns_first_page(self):
        self.create_sixteen_published_events()

        response = self.client.get(
            reverse('list_events'),
            data={'page': 'invalid'}
        )

        event_page = response.context['event_list']

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, event_page.number)
        self.assertEqual(15, len(event_page))

    def test_page_above_range_returns_last_page(self):
        self.create_sixteen_published_events()

        response = self.client.get(
            reverse('list_events'),
            data={'page': 9999}
        )

        event_page = response.context['event_list']

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, event_page.number)
        self.assertEqual(1, len(event_page))

    def test_past_events_returns_the_expected_event(self):
        self.create_published_event(
            title='Future Event'
        )
        self.create_published_event(
            title='Past Event',
            closing_date=now() - timedelta(days=7)
        )

        response = self.client.get(reverse('past_events'))

        self.assertEqual(200, response.status_code)
        self.assertQuerysetEqual(
            response.context['event_list'],
            ['<Event: Past Event>']
        )

    def test_search_in_past_events_filters_only_past_events(self):
        self.create_published_event(
        title='Past Python Event',
        description='Conference about Django',
        closing_date=now() - timedelta(days=7)
        )

        self.create_published_event(
            title='Future Python Event',
            description='Conference about Django',
            closing_date=now() + timedelta(days=7)
        )

        self.create_published_event(
            title='Past Java Event',
            description='Conference about Java',
            closing_date=now() - timedelta(days=7)
        )

        response = self.client.get(
            reverse('past_events'),
            data={'search': 'Django'}
        )

        self.assertEqual(200, response.status_code)
        self.assertQuerysetEqual(
            response.context['event_list'],
            ['<Event: Past Python Event>']
        )