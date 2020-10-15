salebox-django
===================

Connect a standalone Django ecommerce website to a https://salebox.io backoffice.

---

## Create a website using salebox-django and wagtail:

Create and enter a virtualenvironment, then:

    pip install wagtail salebox-django psycopg2
    wagtail start <mysite>
    cd <mysite>
    pip install -r requirements.txt

Edit `www/settings/base.py`:

 * Add `'saleboxdjango'` to `INSTALLED_APPS`
 * Add `'saleboxdjango.middleware.SaleboxMiddleware'` to the end of `MIDDLEWARE`
 * Add `'saleboxdjango.middleware.SaleboxI18NSessionStoreMiddleware'` to the end of `MIDDLEWARE` if this is a multi-language site
 * Add `'saleboxdjango.context_processor.salebox'` to `TEMPLATES > OPTIONS`

Make sure we are using postgres:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': '<DATABASE_NAME>',
            'USER': '<DATABASE_USER>',
            'PASSWORD': '<DATABASE_PASSWORD>',
            'HOST': 'localhost',
            'CONN_MAX_AGE': 60,
        }
    }

Add the following to `www/settings/base.py` and fill in the blanks:

    SALEBOX = {
        'ANALYTICS': {
            'SEND': True
        },
        'API': {
            'IP': '<SALEBOX SERVER IP ADDRESS>',
            'URL': '<SALEBOX SERVER URL>',
            'KEY': '<POS KEY>',
            'LICENSE': '<POS LICENSE>',
        },
        'CHECKOUT': {
            'PRE_URL': '/basket/',
            'SEQUENCE': [
                ['shipping_invoice_address', '/checkout/address/', 'Delivery & Invoice Address'],
                ['shipping_method', '/checkout/shipping/', 'Shipping Method'],
                ['confirm', '/checkout/confirm/', 'Confirmation'],
                ['gateway', '/checkout/gateway/', 'Gateway'],
            ],
            'TRANSACTION_DATE': 'payment',
        },
        'IMG': {},
        'MEMBER': {
            'USER_EQUALS_MEMBER': 'MANUAL'
        },
        'MISC': {
            'ALLOWED_COUNTRIES': [],
            'POS_USER_ID': <POS USER ID>,
            'VAT_RATE': <VAT RATE>
        },
        'SESSION': {
            'DEFAULT_PRODUCT_LIST_ORDER': 'rating_high_to_low'
        }
    }

Prepare the database:

    python manage.py migrate
    python manage.py createsuperuser
    python manage.py saleboxsync
    python manage.py runserver

---

## New: Get the latest Maxmind GeoLite2 City database

`cd` to your `/var/www/[my project]` folder, then:

    wget https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz
    tar xvzf GeoLite2-City.tar.gz
    rm GeoLite2-City.tar.gz
    rm -rf geo
    mv GeoLite2-City_* geo
