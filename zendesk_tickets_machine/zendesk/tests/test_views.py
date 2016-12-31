from unittest.mock import call, patch

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from agents.models import Agent
from agent_groups.models import AgentGroup
from tickets.models import Ticket


class ZendeskTicketsCreateViewTest(TestCase):
    @override_settings(DEBUG=True)
    @patch('zendesk.views.ZendeskTicket')
    @patch('zendesk.views.Requester')
    def test_ticket_create_view_should_send_data_to_create_zendesk_ticket(
        self,
        mock_requester,
        mock_ticket
    ):
        mock_ticket.return_value.create.return_value = {
            'ticket': {
                'id': 1
            }
        }
        mock_requester.return_value.search.return_value = {
            'users': [{
                'id': '2'
            }]
        }

        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome pronto_marketing',
            private_comment='Private comment'
        )

        self.client.get(reverse('zendesk_tickets_create'))

        data = {
            'ticket': {
                'subject': 'Ticket 1',
                'comment': {
                    'body': 'Comment 1'
                },
                'requester_id': '2',
                'assignee_id': '123',
                'group_id': '123',
                'type': 'question',
                'priority': 'urgent',
                'tags': ['welcome', 'pronto_marketing']
            }
        }

        comment = {
            'ticket': {
                'comment': {
                    'author_id': '123',
                    'body': 'Private comment',
                    'public': False
                }
            }
        }
        mock_ticket.return_value.create.assert_called_once_with(data)
        mock_ticket.return_value.create_comment.assert_called_once_with(
            comment,
            1
        )

    @override_settings(DEBUG=True)
    @patch('zendesk.views.ZendeskTicket')
    @patch('zendesk.views.Requester')
    def test_ticket_create_view_should_create_two_tickets_if_there_are_two(
        self,
        mock_requester,
        mock_ticket
    ):
        mock_ticket.return_value.create.return_value = {
            'ticket': {
                'id': 1
            }
        }

        mock_requester.return_value.search.return_value = {
            'users': [{
                'id': '2'
            }]
        }

        mock_ticket.return_value.create_comment.return_value = {
            'audit': {
                'events': [{
                    'public': False,
                    'body': 'Private Comment',
                    'author_id': '2'
                }]
            }
        }

        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )

        Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment'
        )
        Ticket.objects.create(
            subject='Ticket 2',
            comment='Comment 2',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='low',
            tags='welcome',
            private_comment='Private comment'
        )

        self.client.get(reverse('zendesk_tickets_create'))

        self.assertEqual(mock_ticket.return_value.create.call_count, 2)
        self.assertEqual(mock_ticket.return_value.create_comment.call_count, 2)

        ticket_calls = [
            call({
                'ticket': {
                    'subject': 'Ticket 1',
                    'comment': {
                        'body': 'Comment 1'
                    },
                    'requester_id': '2',
                    'assignee_id': '123',
                    'group_id': '123',
                    'type': 'question',
                    'priority': 'urgent',
                    'tags': ['welcome']
                }
            }),
            call({
                'ticket': {
                    'subject': 'Ticket 2',
                    'comment': {
                        'body': 'Comment 2'
                    },
                    'requester_id': '2',
                    'assignee_id': '123',
                    'group_id': '123',
                    'type': 'question',
                    'priority': 'low',
                    'tags': ['welcome']
                }
            })
        ]
        mock_ticket.return_value.create.assert_has_calls(ticket_calls)

        comment_calls = [
            call({
                'ticket': {
                    'comment': {
                        'author_id': '123',
                        'body': 'Private comment',
                        'public': False
                    }
                }
            }, 1),
            call({
                'ticket': {
                    'comment': {
                        'author_id': '123',
                        'body': 'Private comment',
                        'public': False
                    }
                }
            }, 1)
        ]
        mock_ticket.return_value.create_comment.assert_has_calls(comment_calls)

    @override_settings(DEBUG=True)
    @patch('zendesk.views.ZendeskTicket')
    def test_ticket_create_view_should_get_http_response_200(self, mock):
        mock.return_value.create.return_value = {
            'ticket': {
                'id': 1
            }
        }

        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment',
            zendesk_ticket_id='24328'
        )

        response = self.client.get(reverse('zendesk_tickets_create'))

        self.assertEqual(response.status_code, 200)

    @override_settings(DEBUG=True)
    @patch('zendesk.views.ZendeskTicket')
    @patch('zendesk.views.Requester')
    def test_it_should_set_zendesk_ticket_id_and_requester_id_to_ticket(
        self,
        mock_requester,
        mock_ticket
    ):
        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        ticket = Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome'
        )

        self.assertIsNone(ticket.zendesk_ticket_id)

        ticket_url = 'https://pronto1445242156.zendesk.com/api/v2/' \
            'tickets/16.json'
        result = {
            'ticket': {
                'subject': 'Hello',
                'submitter_id': 1095195473,
                'priority': None,
                'raw_subject': 'Hello',
                'id': 16,
                'url': ticket_url,
                'group_id': 23338833,
                'tags': ['welcome'],
                'assignee_id': 1095195243,
                'via': {
                    'channel': 'api',
                    'source': {
                        'from': {}, 'to': {}, 'rel': None
                    }
                },
                'ticket_form_id': None,
                'updated_at': '2016-12-11T13:27:12Z',
                'created_at': '2016-12-11T13:27:12Z',
                'description': 'yeah..',
                'status': 'open',
                'requester_id': 1095195473,
                'forum_topic_id': None
            }
        }
        mock_ticket.return_value.create.return_value = result

        mock_requester.return_value.search.return_value = {
            'users': [{
                'id': '1095195473'
            }]
        }

        self.client.get(reverse('zendesk_tickets_create'))

        ticket = Ticket.objects.last()
        self.assertEqual(ticket.zendesk_ticket_id, '16')
        self.assertEqual(ticket.requester_id, '1095195473')

    @patch('zendesk.views.ZendeskTicket')
    def test_create_view_should_not_create_if_zendesk_ticket_id_not_empty(
        self,
        mock
    ):
        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )

        Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment',
            zendesk_ticket_id='123'
        )

        self.client.get(reverse('zendesk_tickets_create'))

        self.assertEqual(mock.return_value.create.call_count, 0)

    @patch('zendesk.views.ZendeskTicket')
    @patch('zendesk.views.Requester')
    def test_create_view_should_not_create_if_requester_id_is_empty(
        self,
        mock_requester,
        mock_ticket
    ):
        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        ticket = Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment'
        )

        self.assertIsNone(ticket.zendesk_ticket_id)

        ticket_url = 'https://pronto1445242156.zendesk.com/api/v2/' \
            'tickets/16.json'
        result = {
            'ticket': {
                'subject': 'Hello',
                'submitter_id': 1095195473,
                'priority': None,
                'raw_subject': 'Hello',
                'id': 16,
                'url': ticket_url,
                'group_id': 23338833,
                'tags': ['welcome'],
                'assignee_id': 1095195243,
                'via': {
                    'channel': 'api',
                    'source': {
                        'from': {}, 'to': {}, 'rel': None
                    }
                },
                'ticket_form_id': None,
                'updated_at': '2016-12-11T13:27:12Z',
                'created_at': '2016-12-11T13:27:12Z',
                'description': 'yeah..',
                'status': 'open',
                'requester_id': '',
                'forum_topic_id': None
            }
        }
        mock_ticket.return_value.create.return_value = result

        mock_requester.return_value.search.return_value = {
            'users': []
        }

        self.client.get(reverse('zendesk_tickets_create'))

        ticket = Ticket.objects.last()
        self.assertIsNone(ticket.zendesk_ticket_id)
        self.assertIsNone(ticket.requester_id)
