from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from decimal import Decimal

# Create your models here.
from account.models import Profile, Order
from django.db.models import Avg,Count

class Campaigns(models.Model):
    campaign_name = models.CharField(max_length=50, null=True, verbose_name='Campaign Name')
    campaign_image = models.ImageField(null=True, blank=True)
    campaign_description = models.TextField(null=True, blank=True)
    campaign_date = models.DateTimeField(auto_now_add=True)
    campaign_slug = models.SlugField(unique=True, verbose_name='Product Slug')
    campaign_items = models.JSONField(blank=True, null=True, verbose_name="camp_items", default=list)
    id = models.AutoField(primary_key=True)
    discount_rate = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    products = models.ManyToManyField('Product', blank=True,related_name='campaigns')
    def __str__(self):
        return self.campaign_name

class Category(models.Model):
    category_name = models.CharField(max_length=50, null=True, verbose_name='Category Name')
    category_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.category_name


class Brand(models.Model):
    brand_name = models.CharField(max_length=50, null=True, verbose_name='Brand Name')
    brand_image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.brand_name


# class Product(models.Model):
# user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#   users = models.ManyToManyField(CustomUser, blank=True, related_name='favorites')
#   name = models.CharField(max_length=200, null=True, blank=True)
#  image = models.ImageField(null=True, blank=True)
# brand = models.CharField(max_length=200,null=True,blank=True)
# category = models.CharField(max_length=200,null=True,blank=True)
#   product_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
#   product_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
#   description = models.TextField(null=True, blank=True)
#   rating = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
#   numReviews = models.IntegerField(null=True, blank=True, default=0)
#    price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
# countInStock = models.IntegerField(null=True, blank=True, default=0)
# createdAt = models.DateTimeField(auto_now_add=True)
#  _id = models.AutoField(primary_key=True, editable=False)
#   comments = models.JSONField(default=list, null=True, blank=True)
#
#   def _str_(self):
#        return self.name

class Product(models.Model):
    # users = models.ManyToManyField(Profile, blank=True)
    product_name = models.CharField(max_length=200, null=True, blank=True)
    #product_image = models.ImageField(null=True, blank=True)
    product_category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    product_brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    product_description = models.TextField(null=True, blank=True)
    product_rating = models.DecimalField(max_digits=7, decimal_places=1, null=True, blank=True)
    product_numReviews = models.IntegerField(null=True, blank=True, default=0)
    product_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    product_countInStock = models.IntegerField(null=True, blank=True, default=0)
    product_createdAt = models.DateTimeField(auto_now_add=True)
    product_slug = models.SlugField(unique=True, verbose_name='Product Slug')
    digital = models.BooleanField(default=False, null=True, blank=True)
    product_pic = models.ImageField(verbose_name='Product Image', blank=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    def get_discounted_price(self):
        if self.campaigns.exists():
            campaign = self.campaigns.first()  # Retrieve the first campaign the product is associated with
            discount_rate = campaign.discount_rate
            return self.product_price - self.product_price * discount_rate

        return self.product_price


    def is_in_campaign(self):
        # Replace this with actual code that checks if this product is in a campaign.
        # This is just a placeholder, as I don't know the specifics of your implementation.
        return Campaigns.objects.filter(products__in=[self]).exists()
    def update_rating(self):
        ratings = Rating.objects.filter(product=self)
        self.product_numReviews = ratings.count()

        print(ratings.count())

        if self.product_numReviews > 0:
            self.product_rating = sum([r.rating for r in ratings]) / self.product_numReviews
        else:
            self.product_rating = 0

        self.save()

    def __str__(self):
        return self.product_name


class PostImage(models.Model):
    post = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)
    product_pic = models.ImageField(upload_to="images")

    def __str__(self):
        return self.post.product_name


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, default=1)
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, null=False, default=1)
    quantity = models.IntegerField(null=True, blank=True, default=0)
    dateAdded = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return str(self.quantity)

    @property
    def get_total(self):
        total = self.product.get_discounted_price() * self.quantity
        return total


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    review_name = models.CharField(max_length=200, null=True, blank=True)
    review_rating = models.IntegerField(null=True, blank=True, default=0)
    review_comment = models.TextField(null=True, blank=True)
    cast_slug = models.SlugField(unique=True, verbose_name='Profile Slug')

    def _str_(self):
        return str(self.review_rating)


class Rating(models.Model):
    RATING_CHOICES = [
        (0, '0'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_rating()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.product.update_rating()

    def __str__(self):
        return f'{self.user.username}: {self.rating}'


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.SET("Product Deleted"), null=True)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, default=1)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # Add this line

    def __str__(self):
        return f'{self.user.username}: {self.content}'
