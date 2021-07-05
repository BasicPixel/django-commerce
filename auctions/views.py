from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from datetime import datetime

from .models import *
from .forms import *

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

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.filter(active=True)
    })

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # get all comments made on a listing
    try:
        comments = Comment.objects.filter(listing=listing)
    except Comment.DoesNotExist:
        comments = None

    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)

        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'watchlist': user.watchlist.all(),
            'form': BidForm(),
            'winner': listing.winner,
            'comments': comments,
        })

    else:
        # if user is not logged in, don't get watchlist or winner
        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'form': BidForm(),
            'comments': comments,
        })


def user_view(request, user_id):
    # get listings made by user, ordered by active listings in descending order
    listings = Listing.objects.filter(owner=user_id).order_by('-active')
    user = User.objects.get(pk=user_id)

    return render(request, 'auctions/user.html', {
        'listings': listings,
        'user': user
    })

# decorator makes the view only work if user is logged in, redirect to login page otherwise
@login_required(redirect_field_name='login')
def create_listing(request):
    if request.method == 'POST':

        form = ListingForm(request.POST)

        if form.is_valid():
            # save form without committing to database
            listing = form.save(commit=False)

            listing.owner = request.user

            listing.save()

            # create Bid object from starting bid value then set current bid to it
            new_bid = Bid.objects.create(value=listing.starting_bid, listing=listing, user=request.user)

            listing.current_bid = new_bid

            # commit all changes
            listing.save()

            return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'auctions/create.html', {
            'form': ListingForm()
        })

@login_required(redirect_field_name='login')
def watchlist(request, user_id):
    user = User.objects.get(pk=user_id)

    return render(request, 'auctions/watchlist.html', {
        'user': user,
        # get current user watchlist ordered descending by active status
        'watchlist': user.watchlist.all().order_by('-active')
    })


@login_required(redirect_field_name='login')
def save_to_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)

    # link listing with user's watchlist
    user.watchlist.add(listing)

    # redirect back to listing page
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required(redirect_field_name='login')
def remove_from_watchlist(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    user = User.objects.get(pk=request.user.id)

    user.watchlist.remove(listing)

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


# delete listing from database completely (different from close)
@login_required(redirect_field_name='login')
def delete(request, listing_id):
    Listing.objects.get(pk=listing_id).delete()

    return HttpResponseRedirect(reverse('index'))


def categories(request):
    categories = []

    # loop over CATEGORIES tuples and add them to a list, then return the list
    for category_tuple in CATEGORIES:
        categories.append(category_tuple[0])
    print(categories)
    return render(request, 'auctions/categories.html', {
        'categories': categories,
    })


def category_view(request, category_name):
    # listings of current category ordered by active status
    listings = Listing.objects.filter(category=category_name).order_by('-active')
    return render(request, 'auctions/category.html', {
        'category': category_name,
        'listings': listings
    })


@login_required(redirect_field_name='login')
def place_bid(request, listing_id):
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid = form.save(commit=False)
            listing = Listing.objects.get(pk=listing_id)
            data = form.cleaned_data
            value = data['value']

            # if value submitted to form is bigger than current bid value, save new bid
            if float(value) > float(listing.current_bid.value):
                bid.listing = listing
                bid.user = request.user
                listing.current_bid = bid
                bid.save()
                listing.save()

            # otherwise, return error page
            else:
                return render(request, 'auctions/bid_value_error.html')

            return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required(redirect_field_name='login')
def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)

    # set winner to current bid owner, set listing to inactive and save
    listing.winner = listing.current_bid.user
    listing.active = False
    listing.save()

    return HttpResponseRedirect(reverse('listing', args=[listing_id]))


@login_required(redirect_field_name='login')
def add_comment(request, listing_id):

    listing = Listing.objects.get(pk=listing_id)

    if request.method == 'POST':
        # get form data, set all required fields and save
        form = CommentForm(request.POST)

        comment = form.save(commit=False)

        comment.creation_date = datetime.now()
        comment.listing = listing
        comment.user = request.user

        comment.save()

        return HttpResponseRedirect(reverse('listing', args=[listing_id]))

    else:
        return render(request, 'auctions/comment_form.html', {
            'form': CommentForm(),
            'listing': listing
        })

def error_404_view(request, exception):
    return render(request, 'auctions/error_404.html')