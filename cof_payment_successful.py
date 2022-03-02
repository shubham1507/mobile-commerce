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

    pending_transactions = OrderPlacedMappig.objects.filter(
                           attachment__isnull=False).filter(
                           cof_payment_successful=False)

    _url = "https://nodes.wavesnodes.com/transactions/address/3PQrxazghZxJmAoLWczjBGpD4hs6gsv7rHq/limit/200"
    r = requests.get(_url)
    waves_transactions = r.json()

    print('------------------CRON-----------------------')
    print(datetime.datetime.now())
    if pending_transactions:
        for pending_transaction in pending_transactions:
            for waves_transaction in waves_transactions[0]:
                if waves_transaction['attachment'] != '':
                    print(waves_transaction)
                    try:
                        if (pending_transaction.price*1000) == waves_transaction['amount'] and pending_transaction.attachment == (base58.b58decode(waves_transaction['attachment']).decode("utf-8")).strip():
                            pending_transaction.cof_payment_successful = True
                            pending_transaction.save()

                            mapping_id = pending_transaction.id
                            cof_send_invoice(mapping_id)
                    except Exception as e:
                        if (pending_transaction.price*1000) == waves_transaction['transfers'][0]['amount'] and pending_transaction.attachment == (base58.b58decode(waves_transaction['attachment']).decode("utf-8")).strip():
                            pending_transaction.cof_payment_successful = True
                            pending_transaction.save()

                            mapping_id = pending_transaction.id
                            cof_send_invoice(mapping_id)
