import json
import tempfile
from decimal import Decimal

import pytz
import requests
import pyqrcode

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Context, Template
from django.template.loader import get_template
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, user_passes_test

from cointrax.models import PaymentAddress, Registration, RegistrationForm


class RegistrationInfo(object):
    def __init__(self):
        self.date_added = None
        self.full_name = ''
        self.email_address = ''
        self.payment_usd = 0
        self.payment_mbtc = 0
        self.received_mbtc = 0
        self.btc_price = 0
        self.btc_address = ''
        self.paid = False

    def get_payment_usd_str(self):
        return '%.2f' % self.payment_usd

    def get_payment_mbtc_str(self):
        return '%.5f' % self.payment_mbtc

    def get_received_mbtc_str(self):
        return '%.5f' % self.received_mbtc

    def get_btc_price_str(self):
        return '%.2f' % self.btc_price


def in_managers_group(user):
    """
    Returns True if the user is in the managers group.
    """
    return user.groups.filter(name='managers').exists()


def index(request):
    if request.method == 'POST':
        # This is a POST request so we need to process the form data.
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Process the form data.
            full_name = form.cleaned_data['full_name']
            email_address = form.cleaned_data['email_address']
            payment_usd = form.cleaned_data['payment_usd']
            btc_price = form.cleaned_data['btc_price']

            # Get the next available payment address.
            address_set = PaymentAddress.objects.filter(available=True)
            if len(address_set) == 0:
                return HttpResponseRedirect(reverse('not_available'))
            payment_address = address_set[0]

            # Mark this payment address as not available.
            payment_address.available = False
            payment_address.save()

            # Create a Registration record.
            registration = Registration()
            registration.full_name = full_name
            registration.email_address = email_address
            registration.payment_usd = payment_usd
            registration.btc_price = btc_price

            # Calculate BTC payment and and store in Satoshis.
            registration.payment_btc = int(payment_usd/btc_price *
                                           100000000)

            registration.btc_address = payment_address.btc_address
            registration.save()

            # Calculate the payment in BTC and mBTC.
            payment_btc = (Decimal(registration.payment_btc) / 100000000).quantize(Decimal('0.00000001'))
            payment_mbtc = (Decimal(registration.payment_btc) / 100000).quantize(Decimal('0.00001'))

            # Create context object for emails.
            c = Context({'registration': registration,
                         'payment_btc': payment_btc,
                         'payment_mbtc': payment_mbtc,
                         'event_name': settings.EVENT_NAME,
                         'hosturl': settings.HOSTURL})

            # Send an email to the registrant.
            reg_text_t = get_template('registrant_email.txt')
            reg_html_t = get_template('registrant_email.html')
            reg_text = reg_text_t.render(c)
            reg_html = reg_html_t.render(c)
            subject = '%s Bitcoin Registration' % settings.EVENT_NAME
            if settings.ENVIRONMENT_NAME:
                subject += ' - %s' % settings.ENVIRONMENT_NAME
            send_mail(subject, reg_text, 'webmaster@goldmoth.com',
                      [registration.email_address], html_message=reg_html)

            # Send an email to each manager.
            notification_list = []
            managers_group = Group.objects.get(name='managers')
            managers = managers_group.user_set.all()
            for manager in managers:
                notification_list.append(manager.email)
            mgr_text_t = get_template('manager_email.txt')
            mgr_html_t = get_template('manager_email.html')
            mgr_text = mgr_text_t.render(c)
            mgr_html = mgr_html_t.render(c)
            subject = '%s Bitcoin Registration (%s)' % (registration.full_name,
                                                        settings.EVENT_NAME)
            if settings.ENVIRONMENT_NAME:
                subject += ' - %s' % settings.ENVIRONMENT_NAME
            send_mail(subject, mgr_text, 'webmaster@goldmoth.com',
                      notification_list, html_message=mgr_html)

            # Redirect to the payment page.
            return HttpResponseRedirect(
                reverse('address', args=([payment_address.btc_address]))
            )
    else:
        # Make sure we have an available bitcoin address for the registrant.
        address_set = PaymentAddress.objects.filter(available=True)
        if len(address_set) == 0:
            return HttpResponseRedirect(reverse('not_available'))

        # Create a blank form.
        form = RegistrationForm()

    return render(request, 'index.html',
                  {'form': form,
                   'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


def btcprice(request):
    r = requests.get('https://blockchain.info/ticker')
    results = {}
    results['timestamp'] = timezone.localtime(timezone.now()).strftime('%m/%d/%Y %H:%M:%S %Z')
    if r.status_code == 200:
        results['successful'] = True
        results['price'] = r.json()['USD']['last']
    else:
        results['successful'] = False
        results['price'] = 0
    json_data = json.dumps(results)
    return HttpResponse(json_data, content_type='application/json')


def address(request, btc_address):
    # Make sure the registration record exists.
    queryset = Registration.objects.filter(btc_address=btc_address)
    if len(queryset) == 0:
        return HttpResponseRedirect(reverse('not_in_system'))

    registration = queryset[0]

    # Calculate the payment in BTC and mBTC.
    payment_btc = (Decimal(registration.payment_btc) / 100000000).quantize(Decimal('0.00000001'))
    payment_mbtc = (Decimal(registration.payment_btc) / 100000).quantize(Decimal('0.00001'))

    return render(request, 'address.html',
                  {'registration': registration,
                   'payment_btc': payment_btc,
                   'payment_mbtc': payment_mbtc,
                   'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


def qrcode(request):
    address = request.GET.get('address', None)
    amount = request.GET.get('amount', None)
    label = request.GET.get('label', None)

    # Create a temporary file.
    qrcode_file = tempfile.NamedTemporaryFile()

    # Create the QR code content.
    content = ('bitcoin:' + address)
    parms = []
    if label:
        parms.append('label=' + label)
    if amount:
        parms.append('amount=' + amount)
    parmstr = '&'.join(parms)
    if parmstr:
        content = '%s?%s' % (content, parmstr)

    # Generate the qR code image.
    qr_code = pyqrcode.create(content)
    qr_code.png(qrcode_file.name, scale=5)
    qrcode_file.seek(0)
    image_data = qrcode_file.read()
    qrcode_file.close()

    # Serve the image.
    return HttpResponse(image_data, content_type="image/png")


def btctrans(request, btc_address):
    # Get the height of the latest block.
    r = requests.get('https://blockchain.info/latestblock')
    current_block_height = None
    if r.status_code == 200:
        if 'height' in r.json():
            try:
                current_block_height = int(r.json()['height'])
            except ValueError:
                current_block_height = None

    # Get transactions for this address.
    r = requests.get('https://blockchain.info/address/%s?format=json' %
                     btc_address)
    results = {}
    results['timestamp'] = timezone.localtime(timezone.now()).strftime('%m/%d/%Y %H:%M:%S %Z')
    results['transactions'] = []
    results['total_received'] = 0
    if r.status_code == 200:
        results['successful'] = True
        if 'txs' in r.json():
            for tx in r.json()['txs']:
                # Determine the number of confirmations for this transaction.
                if not current_block_height:
                    confirmations_str = 'unable to determine confirmations'
                elif 'block_height' in tx:
                    try:
                        confirmations = (current_block_height -
                                         int(tx['block_height']) + 1)
                    except ValueError:
                        # Parse error, so skip this transaction.
                        continue
                    if confirmations == 1:
                        confirmations_str = '1 confirmation'
                    else:
                        confirmations_str = '%s confirmations' % confirmations
                else:
                    confirmations_str = '0 confirmations'

                # Determine the value received and convert to mBTC.
                for txout in tx['out']:
                    if txout['addr'] == btc_address:
                        if 'value' in txout:
                            try:
                                amount = float(txout['value']) / 100000
                            except ValueError:
                                # Parse error, so skip this transaction.
                                continue
                        results['total_received'] += amount
                        results['transactions'].append(['%.5f' % amount,
                                                        confirmations_str])
    else:
        results['successful'] = False
    json_data = json.dumps(results)
    return HttpResponse(json_data, content_type='application/json')


@login_required
@user_passes_test(in_managers_group, login_url='/forbidden/')
def address_report(request):
    available_addresses = PaymentAddress.objects.filter(available=True)
    return render(request, 'address_report.html',
                  {'available_addresses': available_addresses,
                   'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


@login_required
@user_passes_test(in_managers_group, login_url='/forbidden/')
def registration_report(request):
    # Get queryset of registrations and create dictionary.
    registration_dict = {}
    registrations = Registration.objects.order_by('date_added')
    if registrations:
        for registration in registrations:
            registration_info = RegistrationInfo()
            registration_info.date_added = registration.date_added
            registration_info.full_name = registration.full_name
            registration_info.email_address = registration.email_address
            registration_info.payment_usd = registration.payment_usd
            registration_info.payment_mbtc = Decimal(registration.payment_btc) / 100000
            registration_info.btc_price = registration.btc_price
            registration_info.btc_address = registration.btc_address

            registration_dict[registration.btc_address] = registration_info

        # Get transaction information for the BTC addresses.
        r = requests.get('https://blockchain.info/multiaddr?active=%s' %
                         '|'.join(registration_dict.keys()))

        # Store the amount received in mBTC.
        if r.status_code == 200:
            for address_info in r.json()['addresses']:
                amount = address_info['total_received']
                registration_info = registration_dict[address_info['address']]
                registration_info.received_mbtc = Decimal(amount) / 100000
                if registration_info.received_mbtc >= registration_info.payment_mbtc:
                    registration_info.paid = True

        registration_infos = registration_dict.values()
        registration_infos.sort(key=lambda r: r.date_added, reverse=True)
    else:
        registration_infos = []

    return render(request, 'registration_report.html',
                  {'registration_infos': registration_infos,
                   'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


def not_available(request):
    return render(request, 'not_available.html',
                  {'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


def not_in_system(request):
    return render(request, 'not_in_system.html',
                  {'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})


def forbidden(request):
    return render(request, 'forbidden.html',
                  {'event_name': settings.EVENT_NAME,
                   'environment_name': settings.ENVIRONMENT_NAME})
