from django.db import models


# Create your models here.
class Version(models.Model):
    android_version = models.CharField(max_length=50)
    ios_version = models.CharField(max_length=50)
    android_update_required = models.BooleanField(default=False)
    ios_update_required = models.BooleanField(default=False)

    # def __str__(self):
    #     return '{}'.format(self.android_version)

    def __str__(self):
        return self.android_version
