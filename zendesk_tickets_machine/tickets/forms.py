from django import forms

from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = [
            'subject',
            'comment',
            'requester',
            'assignee',
            'group',
            'ticket_type',
            'due_at',
            'priority',
            'tags',
            'private_comment',
            'zendesk_ticket_id',
            'board',
        ]
        widgets = {
            'subject': forms.TextInput(
                attrs={
                    'placeholder': 'Subject',
                    'class': 'form-control'
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'placeholder': 'Comment',
                    'class': 'form-control',
                    'rows': 6
                }
            ),
            'requester': forms.TextInput(
                attrs={
                    'placeholder': 'Requester',
                    'class': 'form-control'
                }
            ),
            'assignee': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'group': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'ticket_type': forms.Select(
                attrs={
                    'class': 'form-control',
                    'onChange': 'check_ticket_type()'
                }
            ),
            'due_at': forms.SelectDateWidget(
                attrs={
                    'class': 'form-control'
                }
            ),
            'priority': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),
            'tags': forms.TextInput(
                attrs={
                    'placeholder': 'Tags',
                    'class': 'form-control'
                }
            ),
            'private_comment': forms.Textarea(
                attrs={
                    'placeholder': 'Private Comment',
                    'class': 'form-control',
                    'rows': 13
                }
            ),
            'board': forms.HiddenInput()
        }

    def save(self, commit=True):
        ticket = super(TicketForm, self).save(commit=False)

        if not ticket.zendesk_ticket_id:
            ticket.zendesk_ticket_id = None

        if commit:
            ticket.save()

        return ticket
