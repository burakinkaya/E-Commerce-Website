from decimal import Decimal

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from account.models import Profile, Adress, Order, Cards
from base.models import Comment, OrderItem
from base.models import Product, Campaigns
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
from django.shortcuts import render, redirect
from datetime import datetime
from django.core.mail import send_mail
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Sum

from django.core.exceptions import ObjectDoesNotExist

from django import template
from datetime import datetime, timedelta


register = template.Library()

@register.filter
def days_since(value):
    if not value:
        return 0
    return (datetime.now() - value).days

def login_request(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not (user.is_salesmanager or user.is_productmanager or user.is_superuser):
                if user.email_verified:
                    login(request, user)
                    next_url = request.GET.get('next')
                    if next_url is None:
                        messages.success(request, "Login Successful!")
                        return redirect("index")
                    else:
                        return redirect(next_url)
                else:
                    return render(request, "account/verification_sent.html")
            else:
                messages.error(request, "This is an admin account.")
                return render(request, "account/login.html")
        else:
            messages.error(request, "Username or Password is not valid.")
            return render(request, "account/login.html")

    else:
        return render(request, "account/login.html")


def send_verification_email(request, user):
    token = user.generate_verification_token()
    verification_link = request.build_absolute_uri(
        reverse('verify_user', args=[token]))

    context = {
        'user_name': user.first_name,  # assuming the user's name is stored in 'first_name'
        'verification_link': verification_link
    }

    html_message = render_to_string('account/verification_email.html', context)
    plain_message = strip_tags(html_message)

    send_mail(
        'Welcome, ' + user.first_name,
        plain_message,
        'burakinkaya0@gmail.com',
        [user.email],
        fail_silently=False,
        html_message=html_message,
    )


def verify_user(request, token):
    user = get_object_or_404(Profile, email_verification_token=token)
    user.email_verified = True
    user.save()
    return HttpResponseRedirect(reverse('verified'))


# yapıyı degıstır
def register_request(request):
    if request.method == "POST":
        username = request.POST.get("username", None)
        email = request.POST.get("email", None)
        first_name = request.POST.get("first_name", None)
        last_name = request.POST.get("last_name", None)
        birthdate = request.POST.get("birthdate", None)
        password = request.POST.get("password", None)
        re_password = request.POST.get("repassword", None)
        gender = request.POST.get("gender", None)

        if password == re_password:
            if Profile.objects.filter(username=username).exists():
                return render(request, "account/register.html", {"error": "Username has already exists."})
            else:
                if Profile.objects.filter(email=email).exists():
                    return render(request, "account/register.html", {"error": "Email has already exists."})
                else:
                    user = Profile(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name, birthdate=birthdate,
                        gender=gender
                    )
                    try:
                        user.full_clean()
                    except Exception as e:
                        return render(request, "account/register.html",
                                      {"error": e.messages})
                    user = Profile.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name, birthdate=birthdate,
                        gender=gender
                    )
                    user.is_active = True
                    user.save()
                    send_verification_email(request, user)
                    return render(request, "account/verification_sent.html")
        else:
            return render(request, "account/register.html", {"error": "Passwords are not the same."})
    else:
        return render(request, "account/register.html")


def verified(request):
    return render(request, 'account/verified.html')


def logout_request(request):
    logout(request)
    messages.success(request, "You have been logging out.")
    return redirect("index")


def profile(request):

    user = request.user
    if request.user.is_salesmanager or request.user.is_productmanager or request.user.is_superuser:
        return render(request, "account/profile2.html")
    else:
        return render(request, "account/profile.html")


def address(request):
    addresses = Adress.objects.all()
    return render(request, 'account/address.html', {'addresses': addresses})


def card(request):

    cards = Cards.objects.all()
    return render(request, 'account/card.html', {'cards': cards})


def admin_page(request):
    user = request.user
    if user.is_salesmanager or user.is_productmanager or user.is_superuser:
        return render(request, "account/admin_page.html")
    else:
        return redirect("profile")


def admin_comments(request):
    user = request.user
    comments = Comment.objects.all()
    if user.is_productmanager or user.is_superuser:
        return render(request, "account/admin_comments.html", {'comments': comments})
    else:
        return redirect("profile")


def admin_orders(request):
    user = request.user
    orders = Order.objects.all()
    order_items = OrderItem.objects.all()
    if user.is_productmanager  or user.is_superuser:
        return render(request, "account/admin_orders.html", {'orders': orders, 'order_items': order_items})
    else:
        return redirect("profile")


def admin_stock(request):
    user = request.user
    products = Product.objects.all()

    if user.is_productmanager or user.is_superuser:
        return render(request, "account/admin_stock.html", {'products': products})
    else:
        return redirect("profile")


def changepassword(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password is successfully changed")
            if request.user.is_salesmanager or request.user.is_superuser or request.user.is_superuser:
                return redirect("changepassword2")
            else:
                return redirect("changepassword")
        else:
            if request.user.is_salesmanager or request.user.is_superuser or request.user.is_superuser:
                return render(request, 'account/changepassword2.html', {"form": form})
            else:
                return render(request, 'account/changepassword.html', {"form": form})

    form = PasswordChangeForm(request.user)
    if request.user.is_salesmanager or request.user.is_superuser or request.user.is_superuser:
        return render(request, 'account/changepassword2.html', {"form": form})
    else:
        return render(request, 'account/changepassword.html', {"form": form})


def add_to_favorites(request, slug):
    # Get the logged-in user
    user = request.user

    # Get the product based on the provided product_id
    # product = Product.objects.get(product_slug=slug)
    if (slug in user.favourite):
        user.favourite.remove(slug)

    else:
        user.favourite.append(slug)

    # Add the product to the user's favorites

    user.save()
    # Redirect back to the product details page or any desired page
    return redirect('/details/' + slug + '/')

def add_to_favorites2(request, slug):
    # Get the logged-in user
    user = request.user

    # Get the product based on the provided product_id
    # product = Product.objects.get(product_slug=slug)
    if (slug in user.favourite):
        user.favourite.remove(slug)

    else:
        user.favourite.append(slug)

    # Add the product to the user's favorites

    user.save()
    # Redirect back to the product details page or any desired page
    return redirect("products")

def add_address(request):
    if request.method == 'POST':
        addresname = request.POST.get('addresname')
        city = request.POST.get('city')
        province = request.POST.get('province')
        street = request.POST.get('street')
        zip = request.POST.get('zip')
        phone = request.POST.get('phone')

        new_address = Adress(addresname=addresname, city=city, province=province, street=street, zip=zip, phone=phone,
                             user=request.user)
        new_address.save()

        messages.success(request, "Address added successfully!")

        addresses = Adress.objects.all()
        return redirect('/account/address' + '/', {'addresses': addresses})
    else:
        addresses = Adress.objects.all()
        return redirect('/account/address' + '/', {'addresses': addresses})


def delete_address(request, id):
    # Get the logged-in user
    user = request.user

    # Get the product based on the provided product_id

    address = Adress.objects.get(id=id)

    address.delete()

    messages.success(request, "Address deleted successfully!")
    # Add the product to the user's favorites
    addresses = Adress.objects.all()
    # Redirect back to the product details page or any desired page
    return redirect('/account/address' + '/', {'addresses': addresses})


def add_card(request):

    if request.method == 'POST':
        cardName = request.POST.get('cardName')
        cardNumber = request.POST.get('cardNumber')
        expiration = request.POST.get('expiration')
        cvc = request.POST.get('cvc')
        cardNick = request.POST.get('cardNick')

        new_card = Cards(cardName=cardName, cardNumber=cardNumber, expiration=expiration, cvc=cvc, cardNick=cardNick,
                         user=request.user)
        new_card.save()

        messages.success(request, "Credit card added successfully!")

        cards = Cards.objects.all()
        return redirect('/account/card' + '/', {'cards': cards})
    else:
        cards = Cards.objects.all()
        return redirect('/account/card' + '/', {'cards': cards})


def delete_card(request, id):

    # Get the logged-in user
    user = request.user

    # Get the product based on the provided product_id

    card = Cards.objects.get(id=id)

    card.delete()

    messages.success(request, "Credit card deleted successfully!")
    # Add the product to the user's favorites
    cards = Cards.objects.all()
    # Redirect back to the product details page or any desired page
    return redirect('/account/card' + '/', {'cards': cards})


def comment_approval(request, comment_id):  # make sure to include 'comment_id' as a parameter
    if request.method == 'POST':
        comment = Comment.objects.get(pk=comment_id)
        is_approved = 'is_approved' in request.POST  # Checkboxes only appear in POST data when checked
        comment.is_approved = is_approved
        comment.save()
        return redirect("admin_comments")
    # Rest of your view function here


def comment_approval_detailed(request, comment_id):  # make sure to include 'comment_id' as a parameter
    if request.method == 'POST':
        comment = Comment.objects.get(pk=comment_id)
        is_approved = 'is_approved' in request.POST  # Checkboxes only appear in POST data when checked
        comment.is_approved = is_approved
        comment.save()

        product = Product.objects.get(product_slug=comment.product.product_slug)
        user = request.user
        comments = Comment.objects.filter(product=product)
        if user.is_salesmanager or user.is_superuser or user.is_superuser:
            return render(request, "base/manage_comments.html", {'comments': comments, 'product': product})
        else:
            return redirect("index")

    # Rest of your view function here


@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    status = request.POST.get('status')

    status_message = ""
    if status == 'processing':
        order.complete = True
        order.in_transit = False
        order.delivered = False
        status_message = "Your order is now in processing state."
    elif status == 'in_transit':
        order.complete = True
        order.in_transit = True
        order.delivered = False
        status_message = "Your order is now in transit."

    elif status == 'delivered':
        order.complete = True
        order.in_transit = True
        order.delivered = True
        orderitems = order.get_products
        for product in orderitems:
            newuser = order.customer
            newuser.purchased_products.add(product)
        status_message = "Your order has been delivered."

    order.save()

    # Create email content with HTML template
    context = {
        'user_name': order.customer.first_name,
        'status_message': status_message,
        'order_id': order.id,
        'order_items': order.orderitem_set.all(),  # Change this line to match your model structure
    }

    print(order.get_products)

    html_message = render_to_string('account/order_status_update_email.html', context)
    plain_message = strip_tags(html_message)

    # Send email
    send_mail(
        'Order Status Update',
        plain_message,
        'burakinkaya0@gmail.com',
        [order.customer.email],
        fail_silently=False,
        html_message=html_message,
    )

    return redirect('admin_orders')


@require_POST
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    new_price = request.POST.get('new_price')
    new_stock = request.POST.get('new_stock')
    new_cost = request.POST.get('new_cost')
    ex_price = product.product_price
    if new_price:
        product.product_price = new_price

    if new_stock:
        product.product_countInStock = new_stock
    if new_cost:
        product.cost = new_cost
    product.save()

    users = Profile.objects.all()

    if new_price:
        if ex_price > Decimal(new_price):
            for user in users:
                if product.product_slug in user.favourite:
                    discount = ex_price - Decimal(new_price)
                    # Create email content with HTML template
                    status_message = "Good news! A product from your favourites list is now on discount! Check the stock before it is too late!"
                    context = {
                        'user_name': user.first_name,
                        'status_message': status_message,
                        'product': product,  # Change this line to match your model structure
                        'discount': discount,
                    }

                    html_message = render_to_string('account/discount.html', context)
                    plain_message = strip_tags(html_message)

                    # Send email
                    send_mail(
                        'Order Status Update',
                        plain_message,
                        'burakinkaya0@gmail.com',
                        [user.email],
                        fail_silently=False,
                        html_message=html_message,
                    )


    if request.user.is_salesmanager:
        return redirect('admin_price')
    elif request.user.is_productmanager:
        return redirect('admin_stock')
    else:
        return redirect('profile')

@require_POST
def update_product_detailed(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    new_price = request.POST.get('new_price')
    new_stock = request.POST.get('new_stock')
    new_cost = request.POST.get('new_cost')
    ex_price = product.product_price
    if new_price:
        product.product_price = new_price

    if new_stock:
        product.product_countInStock = new_stock
    if new_cost:
        product.cost = new_cost
    product.save()
    data = Product.objects.get(product_slug=product.product_slug)
    user = request.user
    comments = data.comment_set.filter(is_approved=True)
    users = Profile.objects.all()
    if new_price:
        if ex_price > Decimal(new_price):
            for user in users:
                if product.product_slug in user.favourite:
                    discount = ex_price - Decimal(new_price)
                    # Create email content with HTML template
                    status_message = "Good news! A product from your favourites list is now on discount! Check the stock before it is too late!"
                    context = {
                        'user_name': user.first_name,
                        'status_message': status_message,
                        'product': product,  # Change this line to match your model structure
                        'discount': discount,
                    }

                    html_message = render_to_string('account/discount.html', context)
                    plain_message = strip_tags(html_message)

                    # Send email
                    send_mail(
                        'Order Status Update',
                        plain_message,
                        'burakinkaya0@gmail.com',
                        [user.email],
                        fail_silently=False,
                        html_message=html_message,
                    )
    context = {
        "data": data,
        "user": user,
        "has_comments": comments.exists()  # here we add a boolean indicating if there are any comments
    }

    data.product_count_range = range(1, data.product_countInStock + 1)

    return redirect('details2', slug=product.product_slug)


def admin_login(request):
    if request.user.is_staff:
        return redirect("index")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        # Check if the user is authenticated
        if user is not None:
            # Now you can safely check if the user is a staff member
            if user.is_superuser or user.is_productmanager or user.is_salesmanager:
                login(request, user)
                nextUrl = request.GET.get('next', None)
                if nextUrl is None:
                    messages.success(request, "Login Successful!")
                    return redirect("index2")
                else:
                    return redirect(nextUrl)
            else:
                messages.error(request, "You are not an admin.")
                return render(request, "account/admin_login.html")
        else:
            messages.error(request, "Username or Password is not valid.")
            return render(request, "account/admin_login.html")

    else:
        return render(request, "account/admin_login.html")


def super_admin(request):
    user = request.user
    all_users = Profile.objects.all()
    if user.is_superuser:
        return render(request, "account/super_admin.html", {'all_users': all_users})
    else:
        return redirect("profile")


def make_admin(request, username):
    user = get_object_or_404(Profile, username=username)
    if request.method == 'POST':
        is_productmanager = request.POST.get('is_productmanager') == 'true'
        is_salesmanager = request.POST.get('is_salesmanager') == 'true'

        # Update user roles. This assumes you have methods set_productmanager() and set_salesmanager() in your User model that accepts a boolean.
        if is_productmanager:
            user.is_productmanager = True
            if not user.is_staff:
                user.is_staff = True
        else:
            user.is_productmanager = False
            if not user.is_salesmanager or user.is_superuser:
                user.is_staff = False
        if is_salesmanager:
            user.is_salesmanager = True
            if not user.is_staff:
                user.is_staff = True
        else:
            user.is_salesmanager = False
            if not user.is_productmanager or user.is_superuser:
                user.is_staff = False
        user.save()

    return redirect("super_admin")
    # redirect or render a template as needed...

    # Handle GET request or other HTTP methods as needed...


def see_receipt(request):
    user = request.user
    return redirect("profile")


def admin_revenue(request):
    now = timezone.now()
    one_day_ago = now - timedelta(days=1)
    one_month_ago = now - timedelta(days=30)
    one_year_ago = now - timedelta(days=365)

    daily_orders = Order.objects.filter(date_ordered__gte=one_day_ago)
    monthly_orders = Order.objects.filter(date_ordered__gte=one_month_ago)
    yearly_orders = Order.objects.filter(date_ordered__gte=one_year_ago)

    subtotal_daily = 0
    subtotal_monthly = 0
    subtotal_yearly = 0
    refund_daily = 0
    refund_monthly = 0
    refund_yearly = 0
    giro_daily = 0
    giro_monthly = 0
    giro_yearly = 0
    income_daily = 0
    income_monthly = 0
    income_yearly = 0
    product_cost_daily = 0
    product_cost_monthly = 0
    product_cost_yearly = 0
    for order in daily_orders:
        if order.is_refunded:
            refund_daily += order.get_cart_total
            giro_daily += order.get_cart_total
            income_daily += order.get_cart_total
        else:
            subtotal_daily += order.get_cart_total
            giro_daily += order.get_cart_total
            income_daily += order.get_cart_total
            allitems = order.orderitem_set.all()
            for item in allitems:
                if item.product.cost is not None and item.quantity is not None:
                    product_cost_daily += (item.product.cost * item.quantity)

    for order in monthly_orders:
        if order.is_refunded:
            refund_monthly += order.get_cart_total
            giro_monthly += order.get_cart_total
            income_monthly += order.get_cart_total
        else:
            subtotal_monthly += order.get_cart_total
            giro_monthly += order.get_cart_total
            income_monthly += order.get_cart_total
            allitems = order.orderitem_set.all()
            for i in allitems:
                if i.product.cost is not None and i.quantity is not None:
                    product_cost_monthly += (i.product.cost * i.quantity)

    for order in yearly_orders:
        if order.is_refunded:
            refund_yearly += order.get_cart_total
            giro_yearly += order.get_cart_total
            income_yearly += order.get_cart_total
        else:
            subtotal_yearly += order.get_cart_total
            giro_yearly += order.get_cart_total
            income_yearly += order.get_cart_total
            allitems = order.orderitem_set.all()
            for i in allitems:
                if i.product.cost is not None and i.quantity is not None:
                    product_cost_yearly += (i.product.cost * i.quantity)

    context = {
        'orders': Order.objects.all(),
        'daily_orders': daily_orders,
        'monthly_orders': monthly_orders,
        'yearly_orders': yearly_orders,
        'subtotal_daily': subtotal_daily,
        'subtotal_monthly': subtotal_monthly,
        'subtotal_yearly': subtotal_yearly,
        'refund_daily': refund_daily,
        'refund_monthly': refund_monthly,
        'refund_yearly': refund_yearly,
        'giro_daily': giro_daily,
        'giro_monthly': giro_monthly,
        'giro_yearly': giro_yearly,
        'income_daily': income_daily,
        'income_monthly': income_monthly,
        'income_yearly': income_yearly,
        'product_cost_daily': product_cost_daily,
        'product_cost_monthly': product_cost_monthly,
        'product_cost_yearly': product_cost_yearly,
    }
    if request.user.is_superuser or request.user.is_salesmanager:
        return render(request, "account/admin_revenue.html", context)
    else:
        return redirect("profile")


def orders(request):
    user = request.user
    orders = Order.objects.all()

    context = {
        'orders': orders,

    }
    return render(request, "account/orders.html", context)


def refund_request(request, order_id):
    order = Order.objects.get(id=order_id)

    order.refund_requested = True
    if not order.delivered:
        order.is_refunded = True
    elif order.delivered:
        # add logic here for when the order is already delivered
        pass

    order.save()

    user = request.user
    orders = Order.objects.all()

    context = {
        'orders': orders,
    }
    return render(request, "account/orders.html", context)


def refund_approval(request, order_id):
    order = Order.objects.get(id=order_id)
    changed = False
    if order.refund_requested:
        if not order.is_refunded:
            order.is_refunded = True
            changed = True
            orderitems = order.orderitem_set.all()
            for item in orderitems:
                item.product.product_countInStock += item.quantity
                item.product.save()
            status_message = "Your refund request has been accepted."
        else:
            order.is_refunded = False
            changed = True
            orderitems = order.orderitem_set.all()
            for item in orderitems:
                item.product.product_countInStock -= item.quantity
                item.product.save()
            status_message = "Your refund cancellation request has been accepted."

    order.save()

    if changed:
        # Create email content with HTML template
        context = {
            'user_name': order.customer.first_name,
            'status_message': status_message,
            'order_id': order.id,
            'order_items': order.orderitem_set.all(),  # Change this line to match your model structure
        }

        print(order.get_products)

        html_message = render_to_string('account/order_status_update_email.html', context)
        plain_message = strip_tags(html_message)

        # Send email
        send_mail(
            'Order Status Update',
            plain_message,
            'burakinkaya0@gmail.com',
            [order.customer.email],
            fail_silently=False,
            html_message=html_message,
        )

    user = request.user
    orders = Order.objects.all()

    context = {
        'orders': orders,

    }

    if user.is_superuser or user.is_salesmanager:
        return render(request, "account/admin_refund.html", context)
    else:
        redirect ("index")


from datetime import datetime

def receipts(request):
    user = request.user
    orders = []

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return redirect("receipts")

        orders = Order.objects.filter(date_ordered__range=[start_date, end_date])

    context = {
        'orders': orders,
    }

    if user.is_superuser or user.is_salesmanager:
        return render(request, "account/receipts.html", context)
    else:
        return redirect("profile")

def campaigns(request):
    user = request.user
    products = Product.objects.all()
    campaigns = Campaigns.objects.all()
    context = {
        'products': products,
        'campaigns': campaigns,

    }
    if user.is_superuser or user.is_salesmanager:
        return render(request, "account/campaigns.html", context)
    else:
        redirect("profile")

def add_campaign(request, slug):
    if request.method == 'POST':
        campaign_id = request.POST['campaign']  # Get the campaign ID from POST data
        product_slug = request.POST['product_slug']  # Get the product slug from POST data

        # Get the actual Campaign and Product instances
        campaign = get_object_or_404(Campaigns, id=campaign_id)
        product = get_object_or_404(Product, product_slug=slug)

        # Add the product to the campaign
        campaign.products.add(product)

        users = Profile.objects.all()  # Get all user profiles
        percentage = campaign.discount_rate*100
        for user in users:
            if product_slug in user.favourite:  # If the product is in user's favourites
                # Create email content with HTML template
                status_message = f"{product.product_name} is now in a {campaign.campaign_name}! Check it out for up to {percentage}% discount!"
                context = {
                    'user_name': user.first_name,
                    'status_message': status_message,
                    'product': product,
                }

                html_message = render_to_string('account/campaign_notification.html', context)
                plain_message = strip_tags(html_message)

                # Send email
                send_mail(
                    'Campaign Alert',
                    plain_message,
                    'burakinkaya0@gmail.com',
                    [user.email],
                    fail_silently=False,
                    html_message=html_message,
                )

        # Redirect user to a success page (replace 'campaigns' with your own URL)
        return redirect('campaigns')



def remove_from_campaign(request, slug):
    if request.method == 'POST':
        campaign_id = request.POST.get('campaign')
        if not campaign_id:
            return HttpResponseBadRequest("Campaign ID is missing in request.")

        product_slug = request.POST.get('product_slug')
        if not product_slug:
            return HttpResponseBadRequest("Product slug is missing in request.")

        # Get the actual Campaign and Product instances
        campaign = get_object_or_404(Campaigns, id=campaign_id)
        product = get_object_or_404(Product, product_slug=slug)

        # Check if the product is in the campaign
        if product in campaign.products.all():
            campaign.products.remove(product)
        else:
            return HttpResponseBadRequest("Product is not in the selected campaign.")

        return redirect('campaigns')


def campaign_pages(request):
    user = request.user
    products = Product.objects.all()
    campaigns = Campaigns.objects.all()
    context = {
        'products': products,
        'campaigns': campaigns,

    }
    return render(request, "account/campaign_pages.html", context)


def admin_price(request):
    user = request.user
    products = Product.objects.all()

    if user.is_salesmanager or user.is_superuser:
        return render(request, "account/admin_price.html", {'products': products})
    else:
        return redirect("profile")


def admin_refund(request):
    user = request.user
    orders = Order.objects.all()
    order_items = OrderItem.objects.all()
    if user.is_salesmanager  or user.is_superuser:
        return render(request, "account/admin_refund.html", {'orders': orders, 'order_items': order_items})
    else:
        return redirect("profile")
