from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=600)
    image_url = models.URLField(blank=True, null=True)
    starting_bid = models.DecimalField(max_digits=6, decimal_places=2, default=1.0)

    active = models.BooleanField(default=True)

    CATEGORIES = (
        ('Laptops & Tablets', 'Laptops & Tablets'),
        ('Desktops', 'Desktops'),
        ('Components & Storage', 'Components & Storage'),
        ('Computer Accessories', 'Computer Accessories'),
        ('Smartphones & Accessories', 'Smartphones & Accessories'),
        ('Smart Watches & Bands', 'Smart Watches & Bands'),
        ('Video Games & Consoles', 'Video Games & Consoles'),
        ('Audio & Headphones', 'Audio & Headphones'),
        ('Printers, Scanners & Supplies', 'Printers, Scanners & Supplies'),
        ('Other', 'Other'),
    )
    category = models.CharField(max_length=64, choices=CATEGORIES, blank=True)

    current_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, related_name='current_bid',blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='buyer', blank=True, null=True)
    watchers = models.ManyToManyField(User, blank=True, related_name='watchlist')


class Bid(models.Model):
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)


class Comment(models.Model):
    value = models.CharField(max_length=200)
    creation_date = models.DateTimeField(blank=True, null=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)