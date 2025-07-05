from django.db import models
from product.models import Product
from django.utils import timezone

# Create your models here.

class Consumer(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        db_table = "consumers"
        verbose_name_plural = "conumers"

        

class Order(models.Model):
    STATUS_CHOICE = [
        ("pending","Pinding"),
        ("canceled", "Canceled"),
        ("accepted", "Accepted"),
        ("arrived", "Arrived"),
    ]
    
    consumer = models.ForeignKey(Consumer , on_delete= models.RESTRICT, related_name="orders")
    
    status = models.CharField(max_length=20,choice= STATUS_CHOICE , default="pending")
    c_date=models.DateTimeField(auto_now_add=True) 
    a_date=models.DateTimeField(null=True , blank=True)
    arr_date=models.DateTimeField(null=True , blank=True)
    
    def change_status(self, new_status):
        self.status = new_status 
        if self.status == "accepted" and self.a_date is None:
            self.a_date = timezone.now()
        elif self.status == "arrived" and self.arr_date is None :
            self.arr_date = timezone.now()
        self.save()


    

