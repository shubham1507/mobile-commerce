import os
from tablib import Dataset

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()

    from django.db import connection
    from apps.accounts.models import Country
    from urllib.request import urlopen
    from bs4 import BeautifulSoup


    converted_prices = []
    prices = {}
    country_list = Country.objects.all()
    for i in range(0, len(country_list)):
        print(i)
        price_converter_page = 'https://www.x-rates.com/calculator/?from=USD'+'&to='+str(country_list[i].currency_symbol)+'&amount=1'
        page = urlopen(price_converter_page)
        soup = BeautifulSoup(page, 'html.parser')
        name_box = soup.find('span', attrs={'class': 'ccOutputRslt'})

        if ',' in name_box.text.split(' ')[0].strip():
            price = name_box.text.split(' ')[0].strip()
            price = price.replace(',','')
            prices['converted_price'] = float(price)
        else:
            prices['converted_price'] = float(name_box.text.split(' ')[0].strip())

        print('Country Name : ' + str(country_list[i].name), 'Rate : ' + str(prices['converted_price']))

        country_list[i].rate = float(round(prices['converted_price'],2))
        country_list[i].save()
