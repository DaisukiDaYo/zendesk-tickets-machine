from unittest.mock import call, patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from ..models import Board
from agents.models import Agent
from agent_groups.models import AgentGroup
from tickets.models import Ticket


class BoardViewTest(TestCase):
    def test_board_view_should_show_board_list(self):
        first_board = Board.objects.create(name='Pre-Production')
        second_board = Board.objects.create(name='Monthly Newsletter')

        response = self.client.get(reverse('boards'))

        expected = '<h1>Boards</h1>'
        self.assertContains(response, expected, status_code=200)

        expected = '<li><a href="%s">%s</a></li>' % (
            reverse(
                'board_single', kwargs={'slug': first_board.slug}
            ),
            first_board.name
        )
        self.assertContains(response, expected, status_code=200)

        expected = '<li><a href="%s">%s</a></li>' % (
            reverse(
                'board_single', kwargs={'slug': second_board.slug}
            ),
            second_board.name
        )
        self.assertContains(response, expected, status_code=200)


class BoardSingleViewTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(name='Natty', zendesk_user_id='456')
        self.agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        self.board = Board.objects.create(name='Pre-Production')
        self.first_ticket = Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='1095195473',
            assignee=self.agent,
            group=self.agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment',
            zendesk_ticket_id='24328',
            board=self.board
        )
        board = Board.objects.create(name='Production')
        self.second_ticket = Ticket.objects.create(
            subject='Ticket 2',
            comment='Comment 2',
            requester='client+another@hisotech.com',
            requester_id='1095195474',
            assignee=self.agent,
            group=self.agent_group,
            ticket_type='question',
            priority='high',
            tags='welcome internal',
            private_comment='Private comment',
            board=board
        )

    def test_board_single_view_should_render_ticket_form(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<form method="post">'
        self.assertContains(response, expected, status_code=200)

        expected = "<input type='hidden' name='csrfmiddlewaretoken'"
        self.assertContains(response, expected, status_code=200)

        expected = '<input id="id_subject" maxlength="300" name="subject" ' \
            'type="text" required />'
        self.assertContains(response, expected, status_code=200)

        expected = '<textarea cols="40" id="id_comment" name="comment" ' \
            'rows="10" required>'
        self.assertContains(response, expected, status_code=200)

        expected = '<input id="id_requester" maxlength="100" ' \
            'name="requester" type="text" required />'
        self.assertContains(response, expected, status_code=200)

        expected = '<select id="id_assignee" name="assignee" required>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="1">Natty</option>'
        self.assertContains(response, expected, status_code=200)

        expected = '<select id="id_group" name="group" required>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="1">Development</option>'
        self.assertContains(response, expected, status_code=200)

        expected = '<select id="id_ticket_type" name="ticket_type" required>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="question">Question</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="incident">Incident</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="problem">Problem</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="task">Task</option>'
        self.assertContains(response, expected, status_code=200)

        expected = '<select id="id_priority" name="priority" required>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="high">High</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="urgent">Urgent</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="normal">Normal</option>'
        self.assertContains(response, expected, status_code=200)
        expected = '<option value="low">Low</option>'
        self.assertContains(response, expected, status_code=200)

        expected = '<input id="id_tags" maxlength="300" name="tags" ' \
            'type="text" />'
        self.assertContains(response, expected, status_code=200)

        expected = '<textarea cols="40" id="id_private_comment" ' \
            'name="private_comment" rows="10" required>'
        self.assertContains(response, expected, status_code=200)

        expected = '<input id="id_zendesk_ticket_id" maxlength="50" ' \
            'name="zendesk_ticket_id" type="text" />'
        self.assertNotContains(response, expected, status_code=200)

        expected = '<input id="id_board" name="board" type="hidden" ' \
            'value="%s" />' % self.board.id
        self.assertContains(response, expected, status_code=200)

        expected = '<input type="submit">'
        self.assertContains(response, expected, status_code=200)

    def test_board_single_view_should_have_table_header(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<th>Subject</th>' \
            '<th>Comment</th>' \
            '<th>Requester</th>' \
            '<th>Assignee</th>' \
            '<th>Group</th>' \
            '<th>Ticket Type</th>' \
            '<th>Priority</th>' \
            '<th>Tags</th>' \
            '<th>Private Comment</th>'
        self.assertContains(response, expected, count=1, status_code=200)

        expected = '<th></th>' \
            '<th>Subject</th>' \
            '<th>Comment</th>' \
            '<th>Requester</th>' \
            '<th>Requester ID</th>' \
            '<th>Assignee</th>' \
            '<th>Group</th>' \
            '<th>Ticket Type</th>' \
            '<th>Priority</th>' \
            '<th>Tags</th>' \
            '<th>Private Comment</th>' \
            '<th>Zendesk Ticket ID</th>'
        self.assertContains(response, expected, count=1, status_code=200)

    def test_board_single_view_should_have_create_tickets_link(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<a href="%s">Create Tickets</a>' % reverse(
            'board_tickets_create',
            kwargs={'slug': self.board.slug}
        )
        self.assertContains(response, expected, count=1, status_code=200)

    def test_board_single_view_should_have_reset_form_link(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<a href="%s">' \
            'Reset Tickets</a>' % reverse(
                'board_reset',
                kwargs={'slug': self.board.slug}
            )
        self.assertContains(response, expected, count=1, status_code=200)

    def test_board_single_view_should_have_board_name(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<h1>%s</h1>' % self.board.name
        self.assertContains(response, expected, status_code=200)

    def test_board_single_view_should_show_ticket_list(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<tr><td><a href="%s">Edit</a> | ' \
            '<a href="%s">Delete</a></td>' \
            '<td>Ticket 1</td><td>Comment 1</td>' \
            '<td>client@hisotech.com</td><td>1095195473</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>urgent</td>' \
            '<td>welcome</td><td>Private comment</td>' \
            '<td><a href="%s" target="_blank">24328</a></td></tr>' % (
                reverse(
                    'ticket_edit',
                    kwargs={'ticket_id': self.first_ticket.id}
                ),
                reverse(
                    'ticket_delete',
                    kwargs={'ticket_id': self.first_ticket.id}
                ),
                settings.ZENDESK_URL + '/agent/tickets/24328'
            )
        self.assertContains(response, expected, status_code=200)

        expected = '<tr><td><a href="/%s/">Edit</a> | ' \
            '<a href="/%s/delete/">Delete</a></td>' \
            '<td>Ticket 2</td><td>Comment 2</td>' \
            '<td>client+another@hisotech.com</td><td>1095195474</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>high</td>' \
            '<td>welcome internal</td>' \
            '<td>Private comment</td>' \
            '<td></td></tr>' % (
                self.second_ticket.id,
                self.second_ticket.id
            )
        self.assertNotContains(response, expected, status_code=200)

    def test_board_single_view_should_save_data_when_submit_ticket_form(self):
        data = {
            'subject': 'Welcome to Pronto Service',
            'comment': 'This is a comment.',
            'requester': 'client@hisotech.com',
            'requester_id': '1095195473',
            'assignee': self.agent.id,
            'group': self.agent_group.id,
            'ticket_type': 'question',
            'priority': 'urgent',
            'tags': 'welcome',
            'private_comment': 'Private comment',
            'zendesk_ticket_id': '24328',
            'board': self.board.id
        }

        response = self.client.post(
            reverse('board_single', kwargs={'slug': self.board.slug}),
            data=data
        )

        ticket = Ticket.objects.last()

        self.assertEqual(ticket.subject, 'Welcome to Pronto Service')
        self.assertEqual(ticket.comment, 'This is a comment.')
        self.assertEqual(ticket.requester, 'client@hisotech.com')
        self.assertEqual(ticket.requester_id, '1095195473')
        self.assertEqual(ticket.assignee.name, 'Natty')
        self.assertEqual(ticket.group.name, 'Development')
        self.assertEqual(ticket.ticket_type, 'question')
        self.assertEqual(ticket.priority, 'urgent')
        self.assertEqual(ticket.tags, 'welcome')
        self.assertEqual(ticket.private_comment, 'Private comment')
        self.assertEqual(ticket.zendesk_ticket_id, '24328')

        expected = '<h1>%s</h1>' % self.board.name
        self.assertContains(response, expected, status_code=200)

        expected = '<tr><td><a href="%s">Edit</a> | ' \
            '<a href="%s">Delete</a></td>' \
            '<td>Ticket 1</td><td>Comment 1</td>' \
            '<td>client@hisotech.com</td><td>1095195473</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>urgent</td>' \
            '<td>welcome</td><td>Private comment</td>' \
            '<td><a href="%s" target="_blank">24328</a></td></tr>' % (
                reverse(
                    'ticket_edit',
                    kwargs={'ticket_id': self.first_ticket.id}
                ),
                reverse(
                    'ticket_delete',
                    kwargs={'ticket_id': self.first_ticket.id}
                ),
                settings.ZENDESK_URL + '/agent/tickets/24328'
            )
        self.assertContains(response, expected, status_code=200)

        expected = '<tr><td><a href="/%s/">Edit</a> | ' \
            '<a href="/%s/delete/">Delete</a></td>' \
            '<td>Ticket 2</td><td>Comment 2</td>' \
            '<td>client+another@hisotech.com</td><td>1095195474</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>high</td>' \
            '<td>welcome internal</td>' \
            '<td>Private comment</td>' \
            '<td></td></tr>' % (
                self.second_ticket.id,
                self.second_ticket.id
            )
        self.assertNotContains(response, expected, status_code=200)


class BoardResetViewTest(TestCase):
    def setUp(self):
        agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        self.board = Board.objects.create(name='Pre-Production')
        self.first_ticket = Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            requester_id='1095195473',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment',
            zendesk_ticket_id='24328',
            board=self.board
        )
        board = Board.objects.create(name='Another Pre-Production')
        self.second_ticket = Ticket.objects.create(
            subject='Ticket 2',
            comment='Comment 2',
            requester='client+another@hisotech.com',
            requester_id='1095195474',
            assignee=agent,
            group=agent_group,
            ticket_type='question',
            priority='high',
            tags='welcome internal',
            private_comment='Private comment',
            zendesk_ticket_id='56578',
            board=board
        )

    def test_reset_view_should_reset_zendesk_ticket_id_for_tickets_in_board(
        self
    ):
        self.client.get(
            reverse('board_reset', kwargs={'slug': self.board.slug})
        )

        first_ticket = Ticket.objects.get(id=self.first_ticket.id)
        self.assertIsNone(first_ticket.zendesk_ticket_id)

        second_ticket = Ticket.objects.get(id=self.second_ticket.id)
        self.assertEqual(second_ticket.zendesk_ticket_id, '56578')

    def test_reset_view_should_redirect_to_board(self):
        response = self.client.get(
            reverse('board_reset', kwargs={'slug': self.board.slug})
        )

        self.assertRedirects(
            response,
            reverse('board_single', kwargs={'slug': self.board.slug}),
            status_code=302,
            target_status_code=200
        )


class BoardZendeskTicketsCreateViewTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(name='Kan', zendesk_user_id='123')
        self.agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        self.board = Board.objects.create(name='Production')
        self.ticket = Ticket.objects.create(
            subject='Ticket 1',
            comment='Comment 1',
            requester='client@hisotech.com',
            assignee=self.agent,
            group=self.agent_group,
            ticket_type='question',
            priority='urgent',
            tags='welcome',
            private_comment='Private comment',
            board=self.board
        )

    @override_settings(DEBUG=True)
    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
    def test_ticket_create_view_should_send_data_to_create_zendesk_ticket(
        self,
        mock_requester,
        mock_ticket
    ):
        ticket = Ticket.objects.last()
        ticket.tags = 'welcome, pronto_marketing'
        ticket.save()

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

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

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
    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
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

        Ticket.objects.create(
            subject='Ticket 2',
            comment='Comment 2',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=self.agent,
            group=self.agent_group,
            ticket_type='question',
            priority='low',
            tags='welcome',
            private_comment='Private comment',
            board=self.board
        )

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

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
    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
    def test_ticket_create_view_should_create_only_tickets_in_their_board(
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

        board = Board.objects.create(name='Monthly Newsletter')
        Ticket.objects.create(
            subject='Ticket 2',
            comment='Comment 2',
            requester='client@hisotech.com',
            requester_id='2',
            assignee=self.agent,
            group=self.agent_group,
            ticket_type='question',
            priority='low',
            tags='welcome',
            private_comment='Private comment',
            board=board
        )

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

        self.assertEqual(mock_ticket.return_value.create.call_count, 1)
        self.assertEqual(mock_ticket.return_value.create_comment.call_count, 1)

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
            }, 1)
        ]
        mock_ticket.return_value.create_comment.assert_has_calls(comment_calls)

    @override_settings(DEBUG=True)
    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
    def test_ticket_create_view_should_redirect_to_board(
        self,
        mock_requester,
        mock_ticket
    ):
        mock_requester.return_value.search.return_value = {
            'users': [{
                'id': '1095195473'
            }]
        }
        mock_ticket.return_value.create.return_value = {
            'ticket': {
                'id': 1
            }
        }

        response = self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

        self.assertRedirects(
            response,
            reverse('board_single', kwargs={'slug': self.board.slug}),
            status_code=302,
            target_status_code=200
        )

    @override_settings(DEBUG=True)
    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
    def test_it_should_set_zendesk_ticket_id_and_requester_id_to_ticket(
        self,
        mock_requester,
        mock_ticket
    ):
        self.assertIsNone(self.ticket.zendesk_ticket_id)

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

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

        ticket = Ticket.objects.last()
        self.assertEqual(ticket.zendesk_ticket_id, '16')
        self.assertEqual(ticket.requester_id, '1095195473')

    @patch('boards.views.ZendeskTicket')
    def test_create_view_should_not_create_if_zendesk_ticket_id_not_empty(
        self,
        mock
    ):
        ticket = Ticket.objects.last()
        ticket.zendesk_ticket_id = '123'
        ticket.save()

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

        self.assertEqual(mock.return_value.create.call_count, 0)

    @patch('boards.views.ZendeskTicket')
    @patch('boards.views.Requester')
    def test_create_view_should_not_create_if_requester_id_is_empty(
        self,
        mock_requester,
        mock_ticket
    ):
        self.assertIsNone(self.ticket.zendesk_ticket_id)

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

        self.client.get(
            reverse('board_tickets_create', kwargs={'slug': self.board.slug})
        )

        ticket = Ticket.objects.last()
        self.assertIsNone(ticket.zendesk_ticket_id)
        self.assertIsNone(ticket.requester_id)
