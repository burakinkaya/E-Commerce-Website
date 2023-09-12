from django.urls import path
from .forms import ProductForm

from . import views
from base import views as secondviews
urlpatterns = [
    path('login/', views.login_request, name="login_request"),
    path('admin_login', views.admin_login, name="admin_login"),
    path('register/', views.register_request, name="register_request"),
    path('logout/', views.logout_request, name="logout_request"),
    path('profile/', views.profile, name="profile"),
    path('profile2/', views.profile, name="profile2"),
    path('changepassword/', views.changepassword, name="changepassword"),
    path('changepassword2/', views.changepassword, name="changepassword2"),
    path('details/<slug:slug>/', secondviews.product_details, name='details'),
    path('details2/<slug:slug>/', secondviews.product_details, name='details2'),
    path('address/', views.address, name="address"),
    path('card/', views.card, name="card"),

    path('add_address/', views.add_address, name="add_address"),
    path('add_card/', views.add_card, name="add_card"),
    path('delete_address/<int:id>/', views.delete_address, name="delete_address"),
    path('delete_card/<int:id>/', views.delete_card, name="delete_card"),
    path('admin_page/', views.admin_page, name="admin_page"),
    path('admin_comments/', views.admin_comments, name="admin_comments"),
    path('admin_orders/', views.admin_orders, name="admin_orders"),
    path('comment_approval/<int:comment_id>/', views.comment_approval, name="comment_approval"),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('admin_stock/', views.admin_stock, name="admin_stock"),
    path('update_product/<int:product_id>/', views.update_product, name='update_product'),
    path('verify/<uuid:token>/', views.verify_user, name='verify_user'),
    path('verified/', views.verified, name="verified"),
    path('comment_approval_detailed/<int:comment_id>/', views.comment_approval_detailed, name="comment_approval_detailed"),
    path('super_admin/', views.super_admin, name="super_admin"),
    path('make_admin/<str:username>/', views.make_admin, name="make_admin"),
    path('see_receipt/', views.see_receipt, name="see_receipt"),
    path('admin_revenue/', views.admin_revenue, name="admin_revenue"),
    path('orders/', views.orders, name="orders"),
    path('wishlist/', secondviews.favourite_products, name="wishlist"),
    path('refund_request/<int:order_id>', views.refund_request, name="refund_request"),
    path('refund_approval/<int:order_id>', views.refund_approval, name="refund_approval"),
    path('get_order_receipt/<int:order_id>', secondviews.get_order_receipt, name='get_order_receipt'),
    path('add_products/', secondviews.add_products, name="add_products"),
    path('add_category/', secondviews.add_category, name='add_category'),
    path('add_brand/', secondviews.add_brand, name='add_brand'),
    path('receipts/', views.receipts, name='receipts'),
    path('campaigns/', views.campaigns, name='campaigns'),
    path('add_campaign/<slug:slug>/', views.add_campaign, name='add_campaign'),
    path('remove_from_campaign/<slug:slug>/', views.remove_from_campaign, name='remove_from_campaign'),
    path('admin_price/', views.admin_price, name="admin_price"),
    path('admin_refund/', views.admin_refund, name="admin_refund"),
]
