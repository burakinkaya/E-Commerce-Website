from django.db import models
from django.contrib.auth.models import User, AbstractUser

from cs308_team6_project import settings

import uuid


# Create your models here.

# class OrderItem(models.Model):
#    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
#    name = models.CharField(max_length=200, null=True, blank=True)
#    quantity = models.IntegerField(null=True, blank=True, default=0)
#    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
#    image = models.CharField(max_length=200, null=True, blank=True)
#    slug#

#    def _str_(self):
#        return self.name


#    order = models.OneToOneField(Order, on_delete=models.CASCADE, null=True, blank=True)
#    address = models.CharField(max_length=200, null=True, blank=True)
#    city = models.CharField(max_length=200, null=True, blank=True)
#    postalCode = models.CharField(max_length=200, null=True, blank=True)
#    country = models.CharField(max_length=200, null=True, blank=True)
#    shippingPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
#    slug

#    def _str_(self):
#        return self.address

class Cart(models.Model):
    cartname = models.CharField(max_length=10, null=True, blank=True, verbose_name='cart')


class Payment(models.Model):
    paymentname = models.CharField(max_length=10, null=True, blank=True, verbose_name='payment')


class Favourite(models.Model):
    favouritename = models.CharField(max_length=10, null=True, blank=True, verbose_name='favorit')


class Profile(AbstractUser):
    gender = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    # name email pass pass
    id  = models.AutoField(primary_key=True)
    birthdate = models.DateField(null=True, verbose_name='Doğum Tarihi')
    gender = models.CharField(max_length=10, choices=gender, null=True, blank=False, verbose_name='Cinsiyet')
    phone = models.IntegerField(null=True, blank=True, verbose_name='tel')
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, verbose_name="payment")
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True, blank=True, verbose_name="cart")
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True, verbose_name="order")
    favourite = models.JSONField(blank=True, null=True, verbose_name="fav", default=list)
    addresses = models.JSONField(blank=True, null=True, verbose_name="adresler", default=list)
    purchased_products = models.ManyToManyField('base.Product', blank=True)
    # commentable = models.JSONField(blank=True, null=True, verbose_name="comment", default=list)
    is_productmanager = models.BooleanField(default=False)  # Add this line
    is_salesmanager = models.BooleanField(default=False)  # Add this line

    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verified = models.BooleanField(default=False)

    def generate_verification_token(self):
        token = uuid.uuid4()
        while Profile.objects.filter(email_verification_token=token).exists():
            token = uuid.uuid4()
        self.email_verification_token = token
        self.save()
        return token

    # adres gender birthdate payment (name surname email nickname password) sepet  favori telefon sipariş
    REQUIRED_FIELDS = ['birthdate', 'gender']

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"


class Adress(models.Model):
    id = models.AutoField(primary_key=True)
    addresname = models.CharField(max_length=100, null=True, blank=True, verbose_name='Address')
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name='City')
    province = models.CharField(max_length=100, null=True, blank=True, verbose_name='Province')
    street = models.CharField(max_length=100, null=True, blank=True, verbose_name='Street')
    zip = models.CharField(max_length=100, null=True, blank=True, verbose_name='Zip')
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Phone')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)


class Cards(models.Model):
    id = models.AutoField(primary_key=True)
    cardName = models.CharField(max_length=30, null=True, blank=True, verbose_name='name')
    cardNumber = models.CharField(max_length=20, null=True, blank=True, verbose_name='number')
    expiration = models.CharField(max_length=10, null=True, blank=True, verbose_name='expiration')
    cvc = models.CharField(max_length=3, null=True, blank=True, verbose_name='cvc')
    cardNick = models.CharField(max_length=30, null=True, blank=True, verbose_name='nick')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    ordername = models.CharField(max_length=10, null=True, blank=True, verbose_name='order')
    customer = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True, null=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    in_transit = models.BooleanField(default=False, null=True, blank=False)
    delivered = models.BooleanField(default=False, null=True, blank=False)
    orderaddress = models.ForeignKey(Adress, on_delete=models.SET_NULL, null=True, blank=True)
    is_refunded = models.BooleanField(default=False, null=True, blank=False)
    refund_requested = models.BooleanField(default=False, null=True, blank=False)

    # paymentMethod = models.CharField(max_length=200, null=True, blank=True)
    # taxPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    # shippingPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    # totalPrice = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    # isPaid = models.BooleanField(default=False)
    # paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    # isDelivered = models.BooleanField(default=False)
    # deliveredAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    # createdAt = models.DateTimeField(auto_now_add=True)
    # slug
    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    @property
    def get_products(self):
        order_items = self.orderitem_set.all()
        products = [item.product for item in order_items]
        return products

    @property
    def get_cart_names(self):
        orderitems = self.orderitem_set.all()
        total = ""
        for item in orderitems:
            total += str(item.quantity) + " piece " + item.product.product_name + " for: " + str(item.get_total) + ", "

        return total

    def get_status(self):
        if self.is_refunded:
            return 'Refunded'
        elif self.delivered:
            return 'Delivered'
        elif self.refund_requested:
            return 'Requested a refund'
        elif self.in_transit:
            return 'In Transit'
        elif self.complete:
            return 'Complete'

        else:
            return None  # Or 'new', or whatever your default status is
    def get_status2(self):
        if self.is_refunded:
            return 'Refunded'
        elif self.delivered:
            return 'Delivered'
        elif self.refund_requested:
            return 'Requested a refund'
        elif self.in_transit:
            return 'In Transit'
        elif self.complete:
            return 'Processing'

        else:
            return None
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if not i.product.digital:
                shipping = True
        return shipping
