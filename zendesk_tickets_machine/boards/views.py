# -*- coding: utf-8 -*-
import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView, View

from .models import Board, BoardGroup
from requesters.models import Requester
from tickets.forms import TicketForm, TicketUpdateOnceForm
from tickets.models import Ticket
from tickets.services import TicketServices
from tickets.tables import TicketTable
from zendesk.api import User as ZendeskRequester
from zendesk.api import Ticket as ZendeskTicket

from django_tables2 import RequestConfig


class BoardView(TemplateView):
    template_name = 'boards.html'

    def get(self, request):
        board_groups = BoardGroup.objects.all()
        boards = Board.objects.all()

        return render(
            request,
            self.template_name,
            {
                'board_groups': board_groups,
                'boards': boards,
            }
        )


class BoardSingleView(TemplateView):
    template_name = 'board_single.html'

    def get(self, request, slug):
        try:
            board = Board.objects.get(slug=slug)
        except Board.DoesNotExist:
            text = 'Oops! The board you are looking for ' \
                'no longer exists..'
            messages.error(request, text)

            return HttpResponseRedirect(reverse('boards'))

        initial = {
            'board': board.id
        }
        form = TicketForm(initial=initial)
        ticketUpdateOnceForm = TicketUpdateOnceForm()
        tickets = TicketTable(
            Ticket.objects.filter(
                board__slug=slug, is_active=True
            ).order_by('id')
        )
        RequestConfig(request).configure(tickets)
        zendesk_ticket_url = settings.ZENDESK_URL + '/agent/tickets/'

        return render(
            request,
            self.template_name,
            {
                'board_name': board.name,
                'board_slug': board.slug,
                'form': form,
                'tickets': tickets,
                'ticketUpdateOnceForm': ticketUpdateOnceForm,
                'zendesk_ticket_url': zendesk_ticket_url
            }
        )

    def post(self, request, slug):
        try:
            board = Board.objects.get(slug=slug)
        except Board.DoesNotExist:
            text = 'Oops! The board you are looking for ' \
                'no longer exists..'
            messages.error(request, text)

            return HttpResponseRedirect(reverse('boards'))

        form = TicketForm(request.POST)
        form.save()

        tickets = TicketTable(
            Ticket.objects.filter(
                board__slug=slug, is_active=True
            ).order_by('id')
        )
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

    def edit_once(self):
        id_list = self.POST.getlist('id_list[]')
        edit_tags = self.POST.get('edit_tags')
        edit_subject = self.POST.get('edit_subject')
        edit_due_at = self.POST.get('edit_due_at')
        edit_assignee = self.POST.get('edit_assignee')
        edit_requester = self.POST.get('edit_requester')

        ticketServices = TicketServices()

        ticketServices.edit_ticket_once(
            id_list,
            edit_tags,
            edit_requester,
            edit_subject,
            edit_due_at,
            edit_assignee
        )

        return HttpResponse(content_type="application/json")


class BoardRequestersResetView(View):
    def get(self, request, slug):
        Ticket.objects.filter(board__slug=slug).update(requester='')

        return HttpResponseRedirect(
            reverse('board_single', kwargs={'slug': slug})
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
        zendesk_user = ZendeskRequester()

        tickets = Ticket.objects.filter(
            board__slug=slug,
            is_active=True
        ).exclude(
            zendesk_ticket_id__isnull=False
        )
        for each in tickets:
            if each.assignee is None or each.requester == '':
                continue

            requester_result = zendesk_user.search(each.requester)
            if each.due_at is not None:
                due_at = each.due_at.isoformat()
            else:
                due_at = ''
            if each.created_by is None:
                created_by = each.assignee.zendesk_user_id
            else:
                created_by = each.created_by.zendesk_user_id
            try:
                requester_id = requester_result['users'][0]['id']
                data = {
                    'ticket': {
                        'subject': each.subject,
                        'comment': {
                            'body': each.comment,
                            'author_id': created_by
                        },
                        'requester_id': requester_id,
                        'assignee_id': each.assignee.zendesk_user_id,
                        'group_id': each.group.zendesk_group_id,
                        'type': each.ticket_type,
                        'due_at': due_at,
                        'priority': each.priority,
                        'tags': [tag.strip() for tag in each.tags.split(',')]
                    }
                }
                result = zendesk_ticket.create(data)
                each.zendesk_ticket_id = result['ticket']['id']
                each.save()

                Requester.objects.get_or_create(
                    email=each.requester,
                    zendesk_user_id=requester_id
                )

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
