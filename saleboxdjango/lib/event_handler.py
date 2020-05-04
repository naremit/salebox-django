import datetime
import requests

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

try:
    from mailqueue.models import MailerMessage
except:
    pass

from saleboxdjango.lib.common import api_auth
from saleboxdjango.models import Event, Member


class SaleboxEventHandler:
    def __init__(self):
        # get list of events
        es = Event \
                .objects \
                .filter(processed_flag=False) \
                .order_by('created')

        # loop through and process them
        for e in es:
            if e.event == 'member_created':
                self.event_member_created(e)
            elif e.event == 'transaction_created':
                self.event_transaction_created(e)
            elif e.event == 'transaction_shipping_packed':
                self.event_transaction_shipping_packed(e)
            elif e.event == 'transaction_shipping_picked':
                self.event_transaction_shipping_picked(e)
            elif e.event == 'transaction_shipping_shipped':
                self.event_transaction_shipping_shipped(e)

    def event_member_created(self, event):
        """
        Add your code here
        Don't forget to set the processed_flag when done
        """
        event.processed_flag = True
        event.save()
        self._sync_member_history(event)

    def event_transaction_created(self, event):
        try:
            t = self._fetch_transaction(event)

            if t['status'] != 'OK':
                return

            # queue email
            email = self._fetch_transaction_email(t)
            if email is not None:
                self._mailqueue(
                    email,
                    render_to_string(
                        'salebox/email/transaction_created/subject.txt',
                        t['transaction']
                    ),
                    render_to_string(
                        'salebox/email/transaction_created/body.txt',
                        t['transaction']
                    ),
                    render_to_string(
                        'salebox/email/transaction_created/body.html',
                        t['transaction']
                    )
                )

            # mark as processed
            event.processed_flag = True
            event.save()
            self._sync_member_history(event)
        except:
            pass

    def event_transaction_shipping_packed(self, event):
        """
        Add your code here
        Don't forget to set the processed_flag when done
        """
        event.processed_flag = True
        event.save()
        self._sync_member_history(event)

    def event_transaction_shipping_picked(self, event):
        """
        Add your code here
        Don't forget to set the processed_flag when done
        """
        event.processed_flag = True
        event.save()
        self._sync_member_history(event)

    def event_transaction_shipping_shipped(self, event):
        try:
            t = self._fetch_transaction(event)
            if t['status'] != 'OK':
                return

            # queue email
            email = self._fetch_transaction_email(t)
            if email is not None:
                self._mailqueue(
                    email,
                    render_to_string(
                        'salebox/email/shipping_shipped/subject.txt',
                        t['transaction']
                    ),
                    render_to_string(
                        'salebox/email/shipping_shipped/body.txt',
                        t['transaction']
                    ),
                    render_to_string(
                        'salebox/email/shipping_shipped/body.html',
                        t['transaction']
                    )
                )

            # mark as processed
            event.processed_flag = True
            event.save()
            self._sync_member_history(event)
        except:
            pass

    def _fetch_member(self, event):
        member = Member \
                    .objects \
                    .filter(salebox_member_id=event.salebox_member_id) \
                    .select_related('parent') \
                    .first()

        user = get_user_model() \
                    .objects \
                    .filter(salebox_member_id=event.salebox_member_id) \
                    .first()

        return {
            'member': member,
            'user': user
        }

    def _fetch_transaction(self, event):
        post = api_auth()
        post['pos_guid'] = event.transaction_guid

        # do request
        url = '%s/api/pos/v2/transaction/fetch' % settings.SALEBOX['API']['URL']
        try:
            r = requests.post(url, data=post)
            o = r.json()
            print(o)
            o['transaction']['dt'] = datetime.datetime(*o['transaction']['dt'])
            return o
        except:
            return None

    def _fetch_transaction_email(self, transaction):
        if transaction['transaction']['customer_email'] is not None:
            return transaction['transaction']['customer_email']

        if transaction['transaction']['member'] is not None and 'email' in transaction['transaction']['member']:
            return transaction['transaction']['member']['email']

        return None

    def _sync_member_history(self, event):
        if event.salebox_member_id is not None:
            m = Member \
                    .objects \
                    .filter(salebox_member_id=event.salebox_member_id) \
                    .first()
            if m is not None:
                m.transactionhistory_request_sync()

    # optional: for use with django-mail-queue
    def _mailqueue(self, to_address, subject, content, html=None, cc=None, bcc=None, from_address=None):
        try:
            MailerMessage
        except:
            return

        # from address
        if from_address is None:
            from_address = settings.DEFAULT_FROM_EMAIL

        # create message
        msg = MailerMessage()
        msg.from_address = from_address
        msg.subject = subject.replace('\n', '').strip()
        msg.to_address = to_address
        msg.content = content
        msg.app = 'Salebox'

        # optional extras
        if html is not None:
            msg.html_content = html
        if cc is not None:
            msg.cc_address = cc
        if bcc is not None:
            msg.bcc_address = bcc

        # save in queue
        msg.save()
