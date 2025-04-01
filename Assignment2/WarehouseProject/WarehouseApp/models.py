from django.db import models

class Item(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PurchaseHeader(models.Model):
    code = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"Purchase {self.code}"

class PurchaseDetail(models.Model):
    purchase = models.ForeignKey(PurchaseHeader, on_delete=models.CASCADE, related_name="details")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        """Override save to update stock and balance when a purchase detail is created"""
        if not self.pk:  
            self.item.stock += self.quantity
            self.item.balance += self.quantity * self.unit_price
            self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"
    

class Sell(models.Model):
    code = models.CharField(max_length=100, unique=True)  
    date = models.DateField() 
    description = models.TextField()  

    def __str__(self):
        return self.code

class SellDetail(models.Model):
    sell = models.ForeignKey(Sell, on_delete=models.CASCADE, related_name='sell_details')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.item.stock < self.quantity:
            raise ValueError("Not enough stock available")
        self.item.stock -= self.quantity
        self.item.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.item.name} - {self.quantity}"

    