from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from ..models import Sheet
from agents.models import Agent
from agent_groups.models import AgentGroup
from tickets.models import Ticket


class SheetViewTest(TestCase):
    def test_ticket_view_should_show_ticket_list(self):
        agent = Agent.objects.create(name='Natty', zendesk_user_id='456')
        agent_group = AgentGroup.objects.create(
            name='Development',
            zendesk_group_id='123'
        )
        sheet = Sheet.objects.create(name='Pre-Production')
        first_ticket = Ticket.objects.create(
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
            sheet=sheet
        )
        second_ticket = Ticket.objects.create(
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
        response = self.client.get(
            reverse('sheet_view', kwargs={'slug': sheet.slug})
        )
        expected = '<tr><td><a href="/%s/">Edit</a> | ' \
            '<a href="/%s/delete/">Delete</a></td>' \
            '<td>Ticket 1</td><td>Comment 1</td>' \
            '<td>client@hisotech.com</td><td>1095195473</td>' \
            '<td>Natty</td><td>Development</td>' \
            '<td>question</td><td>urgent</td>' \
            '<td>welcome</td><td>Private comment</td>' \
            '<td><a href="%s" target="_blank">24328</a></td></tr>' % (
                first_ticket.id,
                first_ticket.id,
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
                second_ticket.id,
                second_ticket.id
            )
        self.assertNotContains(response, expected, status_code=200)
