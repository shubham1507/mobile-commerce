import os
from tablib import Dataset

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'turtle_beans.settings')

    import django
    django.setup()

    from django.db import connection
    from apps.coffee.models import CoffeeImages

    coffee_images = CoffeeImages.objects.all()

    name_list = []
    for coffee_image in coffee_images:
        image_name = coffee_image.image.name
        final_name = image_name.split('CoffeeImages/')[1]
        name_list.append(final_name)


    image_list = os.listdir('/srv/www/turtlebeans-backend/media/CoffeeImages/')

    for image in image_list:
        if image not in name_list:
            os.remove('/srv/www/turtlebeans-backend/media/CoffeeImages/'+str(image))
