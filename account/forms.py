from django import forms
from account.models import Adress, Cards
from base.models import Product,Category ,Brand


from django.core.exceptions import ValidationError

class AddressForm(forms.ModelForm):
    class Meta:
        model = Adress
        fields = ['addresname', 'city', 'province', 'street', 'zip', 'phone']


class CardForm(forms.ModelForm):
    class Meta:
        model = Cards
        fields = ['cardName', 'cardNumber', 'expiration', 'cvc', 'cardNick']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cardName'].label = 'Name on the Card'
        self.fields['cardNumber'].label = 'Number'
        self.fields['expiration'].label = 'Custom Expiration'
        self.fields['cvc'].label = 'CVC'
        self.fields['cardNick'].label = 'Card Nickname'



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_category', 'product_brand', 'product_description',
                  'product_rating', 'product_price', 'product_countInStock',
                  'product_slug', 'digital', 'product_pic', 'cost']

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.fields['product_pic'].required = False

    def clean(self):
        cleaned_data = super().clean()
        pics = self.files.getlist('product_pic')
        if len(pics) < 3:
            raise ValidationError('Please upload at least 3 images.')
        return cleaned_data




class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name', 'category_image']

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['brand_name', 'brand_image']