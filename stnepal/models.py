from django.db import models

# Create your models here.
class Securetech(models.Model):
    name = models.CharField(max_length = 100)
    email = models.EmailField()
    password = models.CharField(max_length = 100)
    phone = models.CharField(max_length=100, null = True)
    is_delete = models.BooleanField(default=False)
    

    class Meta:
        db_table = "securetech_tbl"

    def __str__(self):
        return self.name

