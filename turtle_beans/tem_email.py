import os
import requests
import base58

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()

    import pywaves as pw
    import datetime
    from apps.accounts.views import cof_send_invoice
    from apps.orders.models import OrderPlaced, OrderPlacedMappig
    cof_send_invoice(mapping_id)
