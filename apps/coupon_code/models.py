from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=50,
                            unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    percentage_discount = models.FloatField(validators=[MinValueValidator(0),
                                               MaxValueValidator(100)],
                                            default=0)
    flat_discount = models.FloatField(default=0)
    status = models.BooleanField()

    def __str__(self):
        return self.code
