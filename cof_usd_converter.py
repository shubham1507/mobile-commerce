import os
from tablib import Dataset

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()

    from django.db import connection
    from apps.accounts.models import COFTOUSD
    from urllib.request import urlopen
    from bs4 import BeautifulSoup
    from django.conf import settings

# New scraping code for COF price:
    cof_usd_page = 'https://www.livecoinwatch.com/price/CoffeeCoinUtilityToken-COF'
    page = urlopen(cof_usd_page)
    soup = BeautifulSoup(page, 'html.parser')
    name_box = soup.find('div', attrs={'class': 'content colored'})
    name_box = str(name_box).split('<div ')[2]
    name_box =  name_box.split('$')[1]
    name_box = name_box.split('<')
    usd = float(name_box[0].strip())

#previous code:
    # cof_usd_page = 'https://coinranking.com/coin/coffeecoin-cof'
    # page = urlopen(cof_usd_page)
    # soup = BeautifulSoup(page, 'html.parser')
    # name_box = soup.find('span', attrs={'class': 'price__value'})
    # name_box = str(name_box).split('</span> ')
    # name_box =  name_box[1].split('<span>')[0]
    # name_box = name_box.split('<span')[0]
    # usd = float(name_box.strip())
    destination_address = settings.COF_DESTINATION_ADDRESS

    cof_to_usd_obj = COFTOUSD.objects.get(coin_name='COF')
    cof_to_usd_obj.usd = usd
    cof_to_usd_obj.save()
