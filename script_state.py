# http://v0.postcodeapi.com.au/suburbs/5000.json
countries_list = [
    "Afghanistan",
    "Albania",
    "Algeria",
    "Andorra","Angola","Anguilla","Antigua & Barbuda","Argentina","Armenia","Austria","Azerbaijan","Bahamas","Bahrain","Bangladesh","Barbados","Belarus","Belgium","Belize",
    "Benin","Bermuda","Bhutan","Bolivia","Bosnia & Herzegovina","Botswana","Brazil","Brunei Darussalam","Bulgaria","Burkina Faso","Myanmar/Burma","Burundi","Cambodia",
    "Cameroon","Cape Verde","Cayman Islands","Central African Republic","Chad","Chile","China","Colombia","Comoros","Congo","Costa Rica","Croatia","Cuba","Cyprus",
    "Czech Republic","Democratic Republic of the Congo","Denmark","Djibouti","Dominica","Dominican Republic","Ecuador","Egypt","El Salvador","Equatorial Guinea","Eritrea",
    "Estonia","Ethiopia","Fiji","Finland","France","French Guiana","Gabon","Gambia","Georgia","Germany","Ghana","Great Britain","Greece","Grenada","Guadeloupe","Guatemala",
    "Guinea","Guinea-Bissau","Guyana","Haiti","Honduras","Hungary","Iceland","India","Iran","Iraq","Israel and the Occupied Territories","Italy",
    "Ivory Coast (Cote d'Ivoire)","Jamaica","Japan","Jordan","Kazakhstan","Kenya","Kosovo","Kuwait","Kyrgyz Republic (Kyrgyzstan)","Laos","Latvia","Lebanon","Lesotho",
    "Liberia","Libya","Liechtenstein","Lithuania","Luxembourg","Republic of Macedonia","Madagascar","Malawi","Malaysia","Maldives","Mali","Malta","Martinique","Mauritania",
    "Mauritius","Mayotte","Mexico","Moldova, Republic of","Monaco","Mongolia","Montenegro","Montserrat","Morocco","Mozambique","Namibia","Nepal","Netherlands","New Zealand",
    "Nicaragua","Niger","Nigeria","Korea, Democratic Republic of (North Korea)","Norway","Oman","Pacific Islands","Pakistan","Panama","Papua New Guinea","Paraguay","Peru",
    "Philippines","Poland","Portugal","Puerto Rico","Qatar","Reunion","Romania","Russian Federation","Rwanda","Saint Kitts and Nevis","Saint Lucia",
    "Saint Vincent's & Grenadines","Samoa","Sao Tome and Principe","Saudi Arabia","Senegal","Serbia","Seychelles","Sierra Leone","Singapore","Slovak Republic (Slovakia)",
    "Slovenia","Solomon Islands","Somalia","South Africa","Korea, Republic of (South Korea)","South Sudan","Spain","Sri Lanka","Sudan","Suriname","Swaziland","Sweden",
    "Switzerland","Syria","Tajikistan","Tanzania","Thailand","Timor Leste","Togo","Trinidad & Tobago","Tunisia","Turkey","Turkmenistan","Turks & Caicos Islands","Uganda",
    "Ukraine","United Arab Emirates","Uruguay","Uzbekistan","Venezuela","Vietnam","Virgin Islands (UK)","Virgin Islands (US)","Yemen","Zambia","Zimbabwe"]


import requests
import os

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()

    from django.db import connection
    from apps.accounts.models import Country, State, City

    for i in countries_list:
        Country.objects.create(
            name=str(i),
            group_country_id=2,
            currency_symbol="AUD",
            weight_format="g",
            braintree_merchanr_id="vaibhav_aud"
        )
