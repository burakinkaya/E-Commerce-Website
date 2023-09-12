from django.contrib import admin
from base.models import Profile, Product, Review, Brand, Category, Comment
from .models import *


class PostImageAdmin(admin.StackedInline):
    model = PostImage


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"product_slug": ["product_name"]}
    list_display = ('product_name', 'product_createdAt')
    inlines = [PostImageAdmin]


class CampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {"campaign_slug": ["campaign_name"]}
    list_display = ('campaign_name',)

class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)


admin.site.site_header = "CS308 Admin Panel"
admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Comment)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Campaigns, CampaignAdmin)