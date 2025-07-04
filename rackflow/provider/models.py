from django.db import models


class Provider(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)

    class Meta:
        db_table = "providers"
        verbose_name_plural = "providers"
