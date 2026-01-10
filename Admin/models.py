from django.db import models


class tbl_admin(models.Model):
    admin_name     = models.CharField(max_length=100)
    admin_email    = models.EmailField(unique=True)
    admin_password = models.CharField(max_length=128)   # hash later

    def __str__(self):
        return self.admin_name


