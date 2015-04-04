import os

from django.core.management.base import BaseCommand
from django.conf import settings
from cointrax.models import PaymentAddress


class Command(BaseCommand):
    args = '<btc_addresses_file>'
    help = 'Adds BTC addresses from a file in btc_addresses/ (addresses.txt by default)'

    def handle(self, *args, **options):
        if args:
            address_fname = args[0]
        else:
            address_fname = 'addresses.txt'
        address_fpath = os.path.join(settings.BTC_ADDR_DIR, address_fname)
        if not os.path.exists(address_fpath):
            self.stdout.write('File not found: %s' % address_fpath)
        else:
            # Read the addresses into a list.
            f_addresses = []
            address_file = open(address_fpath)
            for address in address_file:
                address = address.strip()
                if address:
                    f_addresses.append(address)
            address_file.close()
            self.stdout.write('%d addresses read from file' % len(f_addresses))

            # Retrieve a query set of PaymentAddresses create a list of their
            # BTC addresses.
            address_set = PaymentAddress.objects.all()
            p_addresses = []
            for payment_address in address_set:
                p_addresses.append(payment_address.btc_address)

            # Create new PaymentAddress records as required.
            num_added = 0
            for address in f_addresses:
                if address not in p_addresses:
                    num_added += 1
                    payment_address = PaymentAddress()
                    payment_address.btc_address = address
                    payment_address.available = True
                    payment_address.save()
            self.stdout.write('%d addresses added' % num_added)
