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
    print(waves_transactions)
    if pending_transactions:

        for pending_transaction in pending_transactions:
            print('*'*100)
            print(pending_transaction)
            print('*'*100)
            for waves_transaction in waves_transactions[0]:
                if waves_transaction['attachment'] != '':
                    #print(waves_transaction)
                    # try:
                    #     if (int(pending_transaction.price*1000)) == waves_transaction['amount'] and pending_transaction.attachment == base58.b58decode(waves_transaction['attachment']).decode("utf-8"):
                    #         print(pending_transaction.id)
                    #     else:
                    #         print(pending_transaction.id)
                    # except:
                    #     pass
                        # if (int(pending_transaction.price*1000)) == waves_transaction['transfers'][0]['amount'] and pending_transaction.attachment == base58.b58decode(waves_transaction['attachment']).decode("utf-8"):
                        #     print(pending_transaction.id)
                        # else:
                        #     print(pending_transaction.id)
                    try:
                        if (base58.b58decode(waves_transaction['attachment']).decode("utf-8")).strip() == pending_transaction.attachment:
                        # if int(pending_transaction.price*1000) == waves_transaction['amount']:
                            print(pending_transaction.price*1000)
                            print(type(pending_transaction.price*1000))
                            print(int(pending_transaction.price*1000))
                            print(waves_transaction['amount'])
                            print(len(pending_transaction.attachment))
                            print(len((base58.b58decode(waves_transaction['attachment']).decode("utf-8")).strip()))
                        if (int(pending_transaction.price*1000)) == waves_transaction['amount'] and pending_transaction.attachment == (base58.b58decode(waves_transaction['attachment']).decode("utf-8")).strip():
                            pending_transaction.cof_payment_successful = True
                            pending_transaction.save()
                            print(pending_transaction.id)
                            # print(waves_transaction)

                            mapping_id = pending_transaction.id
                            #cof_send_invoice(mapping_id)
                    except Exception as e:
                        # print(waves_transaction['transfers'])
                        try:

                            if (int(pending_transaction.price*1000)) == waves_transaction['transfers'][0]['amount'] and pending_transaction.attachment == base58.b58decode(waves_transaction['attachment']).decode("utf-8"):
                                pending_transaction.cof_payment_successful = True
                                pending_transaction.save()
                                print('*'*100)
                                print(waves_transaction)

                                mapping_id = pending_transaction.id
                                #scof_send_invoice(mapping_id)
                        except:
                            pass
