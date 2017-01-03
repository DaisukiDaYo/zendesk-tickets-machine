import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView, View

from .models import Board, BoardGroup
from tickets.forms import TicketForm
from tickets.models import Ticket
from zendesk.api import User as Requester
from zendesk.api import Ticket as ZendeskTicket


class BoardView(TemplateView):
    template_name = 'boards.html'

    def get(self, request):
        boards = [
            [
                board_group,
                list(Board.objects.filter(board_group=board_group))
            ]
            for board_group in list(BoardGroup.objects.all())
        ]

        return render(
            request,
            self.template_name,
            {
                'boards': boards
            }
        )


class BoardSingleView(TemplateView):
    template_name = 'board_single.html'

    def get(self, request, slug):
        board = Board.objects.get(slug=slug)

        initial = {
            'board': board.id
        }
        form = TicketForm(initial=initial)
        tickets = Ticket.objects.filter(board__slug=slug)
        zendesk_ticket_url = settings.ZENDESK_URL + '/agent/tickets/'

        return render(
            request,
            self.template_name,
            {
                'board_name': board.name,
                'board_slug': board.slug,
                'form': form,
                'tickets': tickets,
                'zendesk_ticket_url': zendesk_ticket_url

            }
        )

    def post(self, request, slug):
        board = Board.objects.get(slug=slug)

        form = TicketForm(request.POST)
        form.save()

        tickets = Ticket.objects.filter(board__slug=slug)
        zendesk_ticket_url = settings.ZENDESK_URL + '/agent/tickets/'

        return render(
            request,
            self.template_name,
            {
                'board_name': board.name,
                'board_slug': board.slug,
                'form': form,
                'tickets': tickets,
                'zendesk_ticket_url': zendesk_ticket_url
            }
        )


class BoardResetView(View):
    def get(self, request, slug):
        Ticket.objects.filter(board__slug=slug).update(zendesk_ticket_id=None)

        return HttpResponseRedirect(
            reverse('board_single', kwargs={'slug': slug})
        )


class BoardZendeskTicketsCreateView(View):
    def get(self, request, slug):
        zendesk_ticket = ZendeskTicket()
        zendesk_user = Requester()

        tickets = Ticket.objects.filter(
            board__slug=slug
        ).exclude(
            zendesk_ticket_id__isnull=False
        )
        for each in tickets:
            requester_result = zendesk_user.search(each.requester)
            try:
                requester_id = requester_result['users'][0]['id']
                data = {
                    'ticket': {
                        'subject': each.subject,
                        'comment': {
                            'body': each.comment
                        },
                        'requester_id': requester_id,
                        'assignee_id': each.assignee.zendesk_user_id,
                        'group_id': each.group.zendesk_group_id,
                        'type': each.ticket_type,
                        'priority': each.priority,
                        'tags': [tag.strip() for tag in each.tags.split(',')]
                    }
                }
                result = zendesk_ticket.create(data)
                each.zendesk_ticket_id = result['ticket']['id']
                each.requester_id = requester_id
                each.save()

                data = {
                    'ticket': {
                        'comment': {
                            'author_id': each.assignee.zendesk_user_id,
                            'body': each.private_comment,
                            'public': False
                        }
                    }
                }
                result = zendesk_ticket.create_comment(
                    data,
                    each.zendesk_ticket_id
                )

            except IndexError:
                pass

            if not settings.DEBUG:
                time.sleep(1)

        return HttpResponseRedirect(
            reverse('board_single', kwargs={'slug': slug})
        )
