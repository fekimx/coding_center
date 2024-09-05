from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import *  # HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm

from .models import AuctionListing, Bid, User, Comment


class ListingForm(ModelForm):
    class Meta:
        model = AuctionListing
        fields = [
            'title',
            'description',
            'category',
            'image',
            'starting_price',
        ]


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

# If the user is not authenticated, render the page with the listings only,
# If he or she is, then render the userswatchlist too.

def index(request):
    if not request.user.is_authenticated:
        return render(request, "auctions/index.html", {
            "listings": AuctionListing.objects.all()
        })
    else:
        return render(request, "auctions/index.html", {
            "listings": AuctionListing.objects.all(),
            "userswatchlist": request.user.watchlist.all()
        })

# If the user is not authenticated, he or she can only see the item details and the comments made.
# Otherwise, the user can see the bid, comment forms and be able to add items to his or her watchlist.

def listing(request, item_id):
    try:
        item = AuctionListing.objects.get(id=item_id)
    except AuctionListing.DoesNotExist:
        raise Http404("The listing does not exist.:/")
    if not request.user.is_authenticated:
        return render(request, "auctions/listing.html", {
            "item": item,
            "comments": item.comments.all(),
        })
    else:
        return render(request, "auctions/listing.html", {
            "item": item,
            "bid_form": BidForm(),
            "comment_form": CommentForm(),
            "comments": item.comments.all(),
            "userswatchlist": request.user.watchlist.all()
        })


@login_required
def watchlist(request, item_id):
    if request.method == "POST":
        item = AuctionListing.objects.get(pk=item_id)
        # If the item is not in the user's watchlist, add; otherwise remove.
        if item not in request.user.watchlist.all():
            request.user.watchlist.add(item)
        else:
            request.user.watchlist.remove(item)
    return HttpResponseRedirect(reverse("listing", args=(item_id,)))

# Render watchlist.html which has all the items the user added to his or her watchlist.

@login_required
def viewwatchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist
    })


@login_required
def createlisting(request):
    return render(request, "auctions/createlisting.html", {
        'listing_form': ListingForm()
    })


def category(request, category):
    return render(request, "auctions/category.html", {
        "category": category,
        "listings": AuctionListing.objects.all()
    })


def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            listing.winner = request.user
            listing.save()
    return HttpResponseRedirect(reverse("index"))


@login_required
def comment(request, item_id):
    if request.method == "POST":
        item = AuctionListing.objects.get(pk=item_id)
        text = request.POST["comment"]
        Comment.objects.create(author=request.user, comment=text, listing=item)
        return HttpResponseRedirect(reverse("listing", args=(item_id,)))
    else:
        return render(request, "auctions/notification.html", {
            "message": "It is not a POST method.",
        })


@login_required
def bid(request, item_id):
    if request.method == "POST":
        item = AuctionListing.objects.get(pk=item_id)
        amount = int(request.POST["amount"])
        current_price = AuctionListing.getCurrentPrice(item)
        #If the amount the user puts is more than the current bid, then add the amount to the list.
        if amount > current_price:
            Bid.objects.create(
                amount=amount, bidder=request.user, listing=item)
            item.winner = request.user
            item.save()
            return HttpResponseRedirect(reverse("listing", args=(item_id,)))
        #If the amount is less than or equal to the current price, then notify the user with a message.
        else:
            return render(request, "auctions/notification.html", {
                "message": "Bid must be higher than the current price.",
            })


def close(request, item_id):
    item = AuctionListing.objects.get(pk=item_id)
    item.status = False
    item.save()
    return render(request, "auctions/notification.html", {
        "message": "You successfuly ended this auction and the winner has been notified.",
    })


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
