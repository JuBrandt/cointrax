Cointrax
========

Cointrax is a Django application which allows visitors to register for an
event, product or service and pay with Bitcoin. Each registrant is assigned a
unique Bitcoin address for payment. Registration information, includding the
unique Bitcoin address, are stored in a database. It includes a report of
people who have registered and their payment status.


Motivation
----------

When accepting Bitcoin, one solution is to present the same address. This
works well for accepting donations, where the identity of the donor does not
matter. When accepting Bitcoin as payment, however, it's important to know
who paid.

Cointrax solves this issue by having a table of Bitcoin addresses, and
assigning each person who registers one of those addresses. These addresses
would be generated by a Bitcoin wallet (not part of cointrax) and loaded
from a text file. Armory, a Bitcoin wallet application written in Python,
can do this easily.


Deployment
----------

If you have not done so, create a Python virtual environment and install
Django. Create a Django project; cointrax will be an application within this
project.

Copy the cointrax directory into your Django project directory.

Add the following lines to the INSTALLED_APPS section in *settings.py*:

    'bootstrap3',
    'captcha',
    'cointrax',

Add the following lines to *settings.py*, making changes as appropriate:

    # Settings for cointrax application

    HOSTURL = 'WEBSITE_URL'
    BTC_ADDR_DIR = '/VENV_DIR/DJANGO_PROJECT_NAME/cointrax/btc_addresses'
    EVENT_NAME = 'EVENT NAME'
    CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
    CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_null',)

    # If this is a test domain, set DOMAIN_NAME to a word like "TEST", and it will
    # be added to the header on each page.
    ENVIRONMENT_NAME = 'TEST'

    # For email testing - remove to use SMTP (the default).
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

Add the following to your urlpatterns in *urls.py*:

    url(r'^cointrax/', include('cointrax.urls')),

Install the required packages:

    pip install -r PROJECT_NAME/cointrax/requirements.txt

Apply the database migrations for the cointrax app:

    python manage.py migrate


Adding Bitcoin Addresses
------------------------

To add addresses to the application, generate a set of addresses from one
of your wallets, and add those addresses to the file
*cointrax/btc_addresses/addresses.txt*. Then run the command:

    python manage.py add_addresses

The addresses will be added to the *PaymentAddress* table. If an address is
already in the table it will not be added again.

By default `add_addresses` reads the file *addresses.txt*. You can specify
a different file:

    python manage.py add_addresses FILE_WITH_BITCOIN_ADDRESSES


Displaying Contact Information
------------------------------

You can add contact information to the *contact.html* template. This will
appear on the main registration page and the address page after the visitor
has registered. This could include who to contact if there are questions
about paying with Bitcoin.


Accessing the Application
-------------------------

Navigate to the */cointrax/* URL in your browser to view the registration
screen.


Reports
-------
*/cointrax/address-report/* lists all unused Bitcoin addresses in the
*PaymentAddress* table.

*/cointrax/registration-report/* lists all the registrations, the
associated Bitcoin addresses, and the amount of Bitcoin sent to those
addresses.

To view these reports you must be authenticated and a member of the
*managers* group.