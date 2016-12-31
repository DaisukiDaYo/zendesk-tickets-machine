from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Board
from agents.models import Agent
from agent_groups.models import AgentGroup
from tickets.models import Ticket


class BoardViewTest(TestCase):
    def test_board_view_should_show_board_list(self):
        first_board = Board.objects.create(name='Pre-Production')
        second_board = Board.objects.create(name='Monthly Newsletter')

        response = self.client.get(reverse('boards'))

        expected = '<title>Boards</title>'
        self.assertContains(response, expected, status_code=200)

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
        agent = Agent.objects.create(name='Natty', zendesk_user_id='456')
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
            private_comment='Private comment'
        )

    def test_board_single_view_should_have_table_header(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

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

        expected = '<a href="%s">' \
            'Create Tickets</a>' % reverse('zendesk_tickets_create')
        self.assertContains(response, expected, count=1, status_code=200)

    def test_board_single_view_should_have_reset_form_link(self):
        response = self.client.get(
            reverse('board_single', kwargs={'slug': self.board.slug})
        )

        expected = '<a href="%s">' \
            'Reset Tickets</a>' % reverse('tickets_reset')
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

        expected = '<tr><td><a href="/%s/">Edit</a> | ' \
            '<a href="/%s/delete/">Delete</a></td>' \
            '<td>Ticket 1</td><td>Comment 1</td>' \
            '<td>client@hisotech.com</td><td>1095195473</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>urgent</td>' \
            '<td>welcome</td><td>Private comment</td>' \
            '<td><a href="%s" target="_blank">24328</a></td></tr>' % (
                self.first_ticket.id,
                self.first_ticket.id,
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
