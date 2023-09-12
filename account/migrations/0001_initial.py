# Generated by Django 4.2.1 on 2023-05-24 12:45

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('birthdate', models.DateField(null=True, verbose_name='Doğum Tarihi')),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True, verbose_name='Cinsiyet')),
                ('phone', models.IntegerField(blank=True, null=True, verbose_name='tel')),
                ('favourite', models.JSONField(blank=True, default=list, null=True, verbose_name='fav')),
                ('addresses', models.JSONField(blank=True, default=list, null=True, verbose_name='adresler')),
                ('is_productmanager', models.BooleanField(default=False)),
                ('is_salesmanager', models.BooleanField(default=False)),
                ('email_verification_token', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('email_verified', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Kullanıcı',
                'verbose_name_plural': 'Kullanıcılar',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cartname', models.CharField(blank=True, max_length=10, null=True, verbose_name='cart')),
            ],
        ),
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('favouritename', models.CharField(blank=True, max_length=10, null=True, verbose_name='favorit')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paymentname', models.CharField(blank=True, max_length=10, null=True, verbose_name='payment')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ordername', models.CharField(blank=True, max_length=10, null=True, verbose_name='order')),
                ('complete', models.BooleanField(default=False, null=True)),
                ('in_transit', models.BooleanField(default=False, null=True)),
                ('delivered', models.BooleanField(default=False, null=True)),
                ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Adress',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('addresname', models.CharField(blank=True, max_length=10, null=True, verbose_name='Address')),
                ('city', models.CharField(blank=True, max_length=20, null=True, verbose_name='City')),
                ('province', models.CharField(blank=True, max_length=20, null=True, verbose_name='Province')),
                ('street', models.CharField(blank=True, max_length=20, null=True, verbose_name='Street')),
                ('zip', models.CharField(blank=True, max_length=10, null=True, verbose_name='Zip')),
                ('phone', models.CharField(blank=True, max_length=10, null=True, verbose_name='Phone')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.cart', verbose_name='cart'),
        ),
        migrations.AddField(
            model_name='profile',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='profile',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.payment', verbose_name='payment'),
        ),
    ]
