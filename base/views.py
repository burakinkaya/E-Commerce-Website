import datetime
import json

from django.core.exceptions import ObjectDoesNotExist

from account.forms import AddressForm, CardForm, CategoryForm, BrandForm
from account.forms import ProductForm

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from base.models import Product, Comment, Order, OrderItem, Rating, Category, PostImage, Campaigns, Brand
import datetime
import json
from account.forms import AddressForm

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from base.models import Product, Comment, Order, OrderItem, Rating, Category, PostImage, Campaigns
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from io import BytesIO

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site

from django.contrib import messages
from django.shortcuts import render, redirect
from account.models import Adress, Cards
from django.urls import reverse

from django.db.models import F
from django.db.models import Avg
from base.utils import cartData

from django.core import serializers


def get_order_items(request):
    if request.user.is_authenticated:
        # Get the latest order by "id" field (or replace "id" with the field name representing the order time)
        order = Order.objects.filter(customer=request.user).latest('id')

        print("Latest order ID: ", order.id)  # Debug print

        # Then get all OrderItems for this order
        order_items = OrderItem.objects.filter(order=order)

        print("Order Items Count: ", order_items.count())  # Debug print

        # Print quantity of each OrderItem
        for item in order_items:
            print(f"Order item: {item.product}, Quantity: {item.quantity}")

        data = serializers.serialize('json', order_items)
        return JsonResponse({'data': data})
    else:
        return JsonResponse({'data': []})


def index(request):
    all_products = Product.objects.all()
    all_campaigns = Campaigns.objects.all()
    # recent_products = Product.order_by('-id')[:6:-1]
    # products_by_review =
    rated_product = Product.objects.order_by('product_rating')
    user = request.user

    context = {
        "all_products": all_products,
        "all_campaigns": all_campaigns,
        "all_categories": Category.objects.all(),
        "rated_product": rated_product
    }

    if user.is_staff:
        messages.error(request, "This is an admin account.")
        return redirect("index2")
    else:
        return render(request, 'base/index.html', context)


def index2(request):
    all_products = Product.objects.all()
    all_campaigns = Campaigns.objects.all()
    # recent_products = Product.order_by('-id')[:6:-1]
    # products_by_review =

    context = {
        "all_products": all_products,
        "all_campaigns": all_campaigns,
    }
    user = request.user
    if user.is_staff:
        return render(request, 'base/index2.html', context)
    else:
        messages.error(request, "You are not an admin.")
        return redirect("index")


def catalog(request):
    if request.method == 'GET':
        q = request.GET['q']
        if q and q is not None:
            q = q
            product = Product.objects.filter(product_name__icontains=q)
            product2 = Product.objects.filter(product_description__icontains=q)
        else:
            return HttpResponse

        context = {
            "product": product,
            "product2": product2,
            "q": q,
        }
        if request.user.is_staff:
            return render(request, 'base/catalog2.html', context)
        else:
            return render(request, 'base/catalog.html', context)


def product_details(request, slug):
    data = Product.objects.get(product_slug=slug)
    user = request.user
    comments = data.comment_set.filter(is_approved=True)
    photos = PostImage.objects.filter(post=data)

    context = {
        "data": data,
        "user": user,
        "has_comments": comments.exists(),
        "photos": photos
    }

    data.product_count_range = range(1, data.product_countInStock + 1)
    if user.is_authenticated:
        if user.is_productmanager or user.is_salesmanager or user.is_superuser:
            return render(request, 'base/product_details2.html', context)
        else:
            return render(request, 'base/product_details.html', context)
    else:
        return render(request, 'base/product_details.html', context)

def favourite_products(request):
    user = request.user
    favourite_product_slugs = user.favourite
    favourite_products = []

    for product_slug in favourite_product_slugs:
        try:
            product = Product.objects.get(product_slug=product_slug)
            favourite_products.append(product)
        except ObjectDoesNotExist:
            # Ignore the product if it does not exist
            pass

    context = {'products': favourite_products}
    return render(request, 'account/wishlist.html', context)


def add_comment(request, slug):
    # Get the logged-in user

    if not request.user.is_authenticated:
        messages.error(request, "You need to login for commenting a product!")
        return redirect('/account/login/')

    user = request.user

    # Get the product based on the provided product_slug
    product = Product.objects.get(product_slug=slug)

    # Check if product is in user's purchased products
    if product not in user.purchased_products.all():
        messages.error(request, "You must purchase a product before you can comment on it.")
        return redirect('/details/' + slug + '/')

    content = request.POST.get('comment')
    if user.is_staff:
        comment = Comment(user=user, product=product, content=content, is_approved=True)
    else:
        comment = Comment(user=user, product=product, content=content)
    comment.save()
    messages.success(request,"Your comment is sent and waiting for approval!")

    return redirect('/details/' + slug + '/')


def delete_comment(request, id):
    # Get the logged-in user
    user = request.user
    # Get the product based on the provided product_id

    comment = Comment.objects.get(id=id)
    slug = comment.product.product_slug
    who = False
    if comment.user != user:
        who = True
    comment.delete()
    # Add the product to the user's favorites
    if who:
        who = False
        return redirect("admin_comments")
    # Redirect back to the product details page or any desired page
    return redirect('/details/' + slug + '/')


def add_rating(request, slug):
    if not request.user.is_authenticated:
        messages.error(request, "You need to login for rating a product!")
        return redirect('/account/login/')

    # Get the logged-in user
    user = request.user

    # Get the product based on the provided product_slug
    product = Product.objects.get(product_slug=slug)

    # Check if product is in user's purchased products
    if product not in user.purchased_products.all():
        messages.error(request, "You must purchase a product before you can rate it.")
        return redirect('/details/' + slug + '/')

    rating_value = request.POST.get('rating')
    rating, created = Rating.objects.get_or_create(user=user, product=product, defaults={'rating': rating_value})
    numReview = product.product_numReviews
    product.product_rating = ( product.product_rating+ int(rating_value))/numReview
    # If rating already exists, don't allow to update
    if not created:
        messages.error(request, "You have already rated this product.")
        return redirect('/details/' + slug + '/')

    messages.success(request, "You have rated this product!")
    return redirect('/details/' + slug + '/')


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    if request.user.is_staff:
        messages.error(request, "This is an admin account.")
        return redirect("index2")
    else:
        return render(request, 'base/cart.html', context)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

        # New Address Form processing
        if request.method == 'POST':
            form = AddressForm(request.POST)
            if form.is_valid():
                new_address = form.save(commit=False)
                new_address.user = request.user
                new_address.save()
                if request.user.is_staff:
                    messages.error(request, "This is an admin account.")
                    return redirect("index2")
                else:
                    return redirect('checkout')  # redirect to the same checkout view after saving the form
        else:
            form = AddressForm()

        # Fetch all addresses related to the current user
        addresses = Adress.objects.filter(user=request.user)

        form2 = CardForm(request.POST)
        if form.is_valid():
            new_card = form.save(commit=False)
            new_card.user = request.user
            new_card.save()
            if request.user.is_staff:
                messages.error(request, "This is an admin account.")
                return redirect("index2")
            else:
                return redirect('checkout')  # redirect to the same checkout view after saving the form

        # Fetch all addresses related to the current user
        cards = Cards.objects.filter(user=request.user)

        context = {
            'items': items,
            'order': order,
            'addresses': addresses,
            'cards': cards,
            'form2': form2,
            'form': form,  # Make sure to include this in the context to display form errors
        }

        for item in order.orderitem_set.all():
            print(f"Product: {item.product.product_name}, Quantity: {item.quantity}")
        if request.user.is_staff:
            messages.error(request, "This is an admin account.")
            return redirect("index2")
        else:
            return render(request, 'base/checkout.html', context)

    else:
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        items = []
        context = {'items': items, 'order': order}
        if request.user.is_staff:
            messages.error(request, "This is an admin account.")
            return redirect("index2")
        else:
            return render(request, 'base/checkout.html', context)


def products(request):
    if request.method == 'POST':
        sort_option = request.POST.get('sorting')  # '1' for price, '2' for rating

        if sort_option == '1':
            products = Product.objects.order_by('-product_price')
        elif sort_option == '2':
            products = Product.objects.order_by('-product_rating')
        elif sort_option == '3':
            products = Product.objects.order_by('product_price')
        elif sort_option == '4':
            products = Product.objects.filter(product_price__range=(0, 500)).order_by('product_price')
        elif sort_option == '5':
            products = Product.objects.filter(product_price__range=(500, 1000)).order_by('product_price')
        elif sort_option == '6':
            products = Product.objects.filter(product_price__range=(1000, 1500)).order_by('product_price')
        elif sort_option == '7':
            products = Product.objects.filter(product_price__range=(1500, 2000)).order_by('product_price')
        elif sort_option == '8':
            products = Product.objects.filter(product_price__range=(2000, 10000)).order_by('product_price')
        else:
            products = Product.objects.all()
    else:
        products = Product.objects.all()

    category = Category.objects.all()
    brands = Brand.objects.all()
    user = request.user
    for product in products:
        product.product_count_range = range(1, product.product_countInStock + 1)

    if user.is_staff:
        return render(request, 'base/products2.html',
                      {'products': products, 'user': user, 'category': category, 'brands': brands})
    else:
        return render(request, 'base/products.html',
                      {'products': products, 'user': user, 'category': category, 'brands': brands})


def filter(request):
    user = request.user
    if request.method == 'POST':
        category_option = request.POST.get('category')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    category = get_object_or_404(Category, category_name=category_option)
    products = Product.objects.filter(product_category=category)


    for product in products:
        product.product_count_range = range(1, product.product_countInStock + 1)

    if user.is_staff:
        return render(request, 'base/filter2.html',
                      {'products': products, 'user': user, 'categories': categories, 'brands': brands})
    else:
        return render(request, 'base/filter.html',
                      {'products': products, 'user': user, 'categories': categories, 'brands': brands})


def brand(request):
    user = request.user
    if request.method == 'POST':
        brand_option = request.POST.get('brand')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    brand = get_object_or_404(Brand, brand_name=brand_option)
    products = Product.objects.filter(product_brand=brand)

    for product in products:
        product.product_count_range = range(1, product.product_countInStock + 1)

    if user.is_staff:
        return render(request, 'base/brand.html',
                      {'products': products, 'user': user, 'categories': categories, 'brands': brands})
    else:
        return render(request, 'base/brand.html',
                      {'products': products, 'user': user, 'categories': categories, 'brands': brands})


def categories(request, category_option):
    user = request.user
    if request.method == 'POST':
        category_option = request.POST.get('category')

    category = get_object_or_404(Category, category_name=category_option)
    brands = Brand.objects.all()
    products = Product.objects.filter(product_category=category)
    categories = Category.objects.all()

    for product in products:
        product.product_count_range = range(1, product.product_countInStock + 1)

    if user.is_staff:
        return render(request, 'base/categories.html', {'products': products, 'user': user, 'categories': categories,'brands': brands})
    else:
        return render(request, 'base/categories.html', {'products': products, 'user': user, 'categories': categories,'brands': brands})


def sort_products(request):
    if request.method == 'POST':
        sort_option = request.POST.get('rating')  # '1' for price, '2' for rating

        if sort_option == '1':
            products = Product.objects.order_by('price')
        elif sort_option == '2':
            products = Product.objects.order_by('-rating')
        else:
            products = Product.objects.all()

        return render(request, 'product_list.html', {'products': products})

    return render(request, 'sort_product.html')


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    quantity = data['quantity']

    customer = request.user
    product = Product.objects.get(product_slug=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
    if action == 'add':
        if quantity is None and orderItem.quantity < product.product_countInStock:
            orderItem.quantity += 1
        elif orderItem.quantity + int(quantity) <= product.product_countInStock:   # Change is here
            orderItem.quantity += int(quantity)
        else:
            orderItem.quantity = product.product_countInStock  # Adjusts quantity to max available stock if exceeded
            messages.error(request, 'Stock Limit Exceeded. The quantity has been adjusted to available stock.')

    elif action == 'remove':
        orderItem.quantity -= 1
        if orderItem.quantity <= 0:
            orderItem.delete()
        messages.success(request, 'You have successfully deleted item from cart')

    elif action == 'removeAll':
        orderItem.quantity = 0
        orderItem.delete()
        messages.success(request, 'You have successfully deleted all items from cart')
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)



def checkout_completed(request):
    if request.method == 'POST':
        selected = False
        created = False
        selected_address_id = request.POST.get('selected_address')

        if selected_address_id:
            # User selected an existing address
            selected_address = Adress.objects.filter(id=selected_address_id).first()
            print('Selected address:', selected_address)
            if selected_address:
                # Use the selected address for checkout
                address_info = {
                    'address_name': selected_address.addresname,
                    'city': selected_address.city,
                    'province': selected_address.province,
                    'street': selected_address.street,
                    'zip': selected_address.zip,
                    'phone': selected_address.phone
                }
                selected = True
            else:
                return render(request, 'base/checkout.html', {'error': 'Invalid address selection'})
        else:
            # User wants to add a new address
            address_info = {
                'address_name': request.POST.get('addresname'),
                'city': request.POST.get('city'),
                'province': request.POST.get('province'),
                'street': request.POST.get('street'),
                'zip': request.POST.get('zip'),
                'phone': request.POST.get('phone')
            }
            created = True

            # Save the new address to the database if it's not empty
            if address_info['address_name'] and address_info['city'] and address_info['province'] and address_info[
                'street'] and address_info['zip'] and address_info['phone']:
                new_address = Adress(
                    user=request.user,
                    addresname=address_info['address_name'],
                    city=address_info['city'],
                    province=address_info['province'],
                    street=address_info['street'],
                    zip=address_info['zip'],
                    phone=address_info['phone']
                )
                new_address.save()
                if not new_address:
                    return render(request, 'base/checkout.html', {'error': 'Failed to save the new address'})

        selected_card_id = request.POST.get('selected_cards')

        if selected_card_id:
            selected_card = Cards.objects.filter(id=selected_card_id).first()
            print('selected_card:', selected_card)
            if selected_card:
                card_info = {
                    'cardName': selected_card.cardName,
                    'cardNumber': selected_card.cardNumber,
                    'expiration': selected_card.expiration,
                    'cvc': selected_card.cvc,
                    'cardNick': selected_card.cardNick,
                }

            else:
                return render(request, 'base/checkout.html', {'error': 'Invalid address selection'})
        else:
            # User wants to add a new address
            card_info = {
                'cardName': request.POST.get('cardName'),
                'cardNumber': request.POST.get('cardNumber'),
                'expiration': request.POST.get('expiration'),
                'cvc': request.POST.get('cvc'),
                'cardNick': request.POST.get('cardNick'),
            }

            # Save the new address to the database if it's not empty
            if card_info['cardName'] and card_info['cardNumber'] and card_info['expiration'] and card_info[
                'cvc'] and card_info['cardNick']:
                new_card = Cards(
                    user=request.user,
                    cardName=card_info['cardName'],
                    cardNumber=card_info['cardNumber'],
                    expiration=card_info['expiration'],
                    cvc=card_info['cvc'],
                    cardNick=card_info['cardNick'],

                )
                new_card.save()

                messages.success(request, "Credit card added successfully!")

        # Get the current order
        order = Order.objects.filter(customer=request.user, complete=False).first()
        if order:
            order.complete = True  # Mark the order as complete
            order.date_ordered = datetime.datetime.now()
            #order.date_ordered = datetime.datetime.now() - datetime.timedelta(days=12)
            if selected:
                order.orderaddress = selected_address
            elif created:
                order.orderaddress = new_address
            order.save()

            # Compute total price
            order_items = order.orderitem_set.all()
            total_price = sum([item.get_total for item in order_items])
            total_items = sum([item.quantity for item in order_items])

            # Retrieve the order items in the cart
            for item in order_items:
                print('Product:', item.product.product_name)
                print('Quantity:', item.quantity)
                print('Price:', item.get_total)
                # request.user.purchased_products.add(item.product)
                print(request.user.purchased_products.all())

                item.product.product_countInStock = F('product_countInStock') - item.quantity
                item.product.save()

            # Create context for templates
            context = {'order_items': order_items, 'total_price': total_price, 'total_items': total_items}
            context['order_id'] = order.id
            context.update({'address_info': address_info})

            status = "Processing"  # default status
            if order.in_transit:
                status = "In Transit"
            if order.delivered:
                status = "Delivered"
            if order.is_refunded:
                status = "Refunded"

            context['order_status'] = status
            print(context['address_info'])
            # Render order summary into a PDF
            template = get_template('base/order_summary_pdf.html')
            html = template.render(context)
            pdf_file = BytesIO()
            status = pisa.CreatePDF(html, dest=pdf_file)

            # Save PDF to disk
            filename = 'order_summary.pdf'
            file_path = f'orders/{filename}'
            pdf_content = ContentFile(pdf_file.getvalue())
            unique_file_path = default_storage.save(file_path, pdf_content)

            absolute_file_path = default_storage.path(unique_file_path)

            # Create email content
            subject = 'Your Order Receipt'
            body = render_to_string('base/email_template.html', context)
            plain_message = strip_tags(body)
            from_email = 'burakinkaya0@gmail.com'
            to = request.user.email

            # Create EmailMessage object
            email = EmailMessage(subject, body, from_email, [to])
            email.content_subtype = "html"  # Here is the magic
            email.attach_file(absolute_file_path)
            email.send()

            # Render the order summary page with the order items
            return render(request, 'base/order_summary.html', context)
        else:
            return render(request, 'base/checkout.html', {'error': 'No items in the cart'})


def edit_product(request, slug):
    user = request.user
    product = Product.objects.get(product_slug=slug)
    if user.is_productmanager or user.is_superuser:
        return render(request, "base/edit_product.html", {'product': product})
    else:
        return redirect("profile")


def manage_comments(request, slug):
    user = request.user
    product = Product.objects.get(product_slug=slug)
    user = request.user
    comments = Comment.objects.filter(product=product)
    if user.is_productmanager or user.is_superuser:
        return render(request, "base/manage_comments.html", {'comments': comments, 'product': product})
    else:
        return redirect("profile")


def delete_comment_detailed(request, id):
    # Get the logged-in user
    user = request.user
    # Get the product based on the provided product_id

    comment = Comment.objects.get(id=id)
    slug = comment.product.product_slug
    product = comment.product
    comments = Comment.objects.filter(product=product)
    comment.delete()
    if user.is_productmanager or user.is_superuser:
        return render(request, "base/manage_comments.html", {'comments': comments, 'product': product})
    else:
        return redirect("index")
    # Add the product to the user's favorites


def campaign(request, slug):
    campaign = Campaigns.objects.get(campaign_slug=slug)
    # recent_products = Product.order_by('-id')[:6:-1]
    # products_by_review =

    context = {
        "campaign": campaign,
    }

    return render(request, 'base/campaigndetails.html', context)


def get_order_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.orderitem_set.all()

    status = "Processing"  # default status
    if order.in_transit:
        status = "In Transit"
    if order.delivered:
        status = "Delivered"
    if order.is_refunded:
        status = "Refunded"
    # Compute total price
    total_price = sum([item.get_total for item in order_items])
    total_items = sum([item.quantity for item in order_items])

    # Create address_info
    order_address = order.orderaddress
    address_info = {
        'address_name': order_address.addresname,
        'city': order_address.city,
        'province': order_address.province,
        'street': order_address.street,
        'zip': order_address.zip,
        'phone': order_address.phone
    }

    # Create context for templates
    context = {'order_items': order_items, 'total_price': total_price, 'total_items': total_items, 'order_id': order.id}
    context.update({'address_info': address_info})
    context['order_status'] = status

    # Render order summary into a PDF
    template = get_template('base/order_summary_pdf.html')
    html = template.render(context)
    pdf_file = BytesIO()
    status = pisa.CreatePDF(html, dest=pdf_file)

    # Serve the PDF directly without saving to disk
    response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=order_{order.id}_summary.pdf'

    return response


def add_products(request):
    user = request.user
    if user.is_productmanager or user.is_superuser:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                product = form.save()
                for f in form.cleaned_data['product_pics']:
                    PostImage.objects.create(post=product, product_pic=f)
                messages.success(request, 'Product added successfully')
                return redirect('products')  # Redirect to your products page
        else:
            form = ProductForm()
        return render(request, "base/add_products.html", {'form': form})
    else:
        return redirect("profile2")






def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully')
            return redirect('admin_page')  # you might need to adjust this depending on your URL configuration
    else:
        form = CategoryForm()
    return render(request, 'base/add_category.html', {'form': form})


def add_brand(request):
    form = BrandForm()
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Brand added successfully')
            return redirect('add_brand')
    context = {'form': form}
    return render(request, 'base/add_brand.html', context)


def delete_product(request, slug):
    user = request.user
    product = Product.objects.get(product_slug=slug)

    if user.is_productmanager or user.is_superuser:
        product.delete()
        return redirect("products")
    else:
        return redirect("profile")
