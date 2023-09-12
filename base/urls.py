from django.urls import path
from . import views
from account import views as secondviews
from .views import sort_products
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.index, name="index"),
    path('admin_main/', views.index2, name="index2"),
    # path('list/<slug:slug>/', views.list, name='list'),
    path('catalog/', views.catalog, name='catalog'),
    path('catalog2/', views.catalog, name='catalog2'),
    path('details/<slug:slug>/', views.product_details, name='details'),
    path('details2/<slug:slug>/', views.product_details, name='details2'),
    path('add-to-favorites/<slug:slug>/', secondviews.add_to_favorites, name="add_to_favorites"),
    path('add-to-favorites2/<slug:slug>/', secondviews.add_to_favorites2, name="add_to_favorites2"),
    path('add-comment/<slug:slug>/', views.add_comment, name="add_comment"),
    path('delete-comment/<int:id>/', views.delete_comment, name='delete_comment'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('products/', views.products, name='products'),
    path('products2/', views.products, name='products'),
    path('update_item/', views.updateItem, name='update_item'),
    path('checkout_completed/', views.checkout_completed, name='checkout_completed'),
    path('add_rating/<slug:slug>/', views.add_rating, name='add_rating'),
    path('filter/', views.filter, name='filter'),
    path('brand/', views.brand, name='brand'),
    path('edit_product/<slug:slug>/', views.edit_product, name='edit_product'),
    path('update_product_detailed/<int:product_id>/', secondviews.update_product_detailed, name='update_product_detailed'),
    path('manage_comments/<slug:slug>/', views.manage_comments, name="manage_comments"),
    path('delete_comment_detailed/<int:id>/', views.delete_comment_detailed, name='delete_comment_detailed'),
    path('categories/<str:category_option>/', views.categories, name='categories'),
    path('get_order_items/', views.get_order_items, name='get_order_items'),
    path('campaign/<slug:slug>', views.campaign, name='campaign'),
    path('add_products/', views.add_products, name="add_products"),
    path('campaign_pages/', secondviews.campaign_pages, name='campaign_pages'),
    path('delete_product/<slug:slug>/', views.delete_product, name='delete_product'),
]
