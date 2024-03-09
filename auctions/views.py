from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .forms import *
from .models import *
from .utils import *



def index(request):
    # print('index', request.session['user_id'])
    if 'user_id' not in request.session:
        request.session['user_id'] = []
    listings = Listing.objects.all().filter(active=True).order_by('-created_at')
    
    return render(request, "auctions/index.html", {
        'listings': listings
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
            request.session['user_id'] = user.id
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    request.session.flush()
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
            request.session['user_id'] = user.id
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user) 
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    user_id = request.session['user_id']
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data['starting_bid']
            image_url = form.cleaned_data['image_url']
            selected_category = form.cleaned_data['category']
            
            try:
                category = Category.objects.get(name=selected_category)
                creator = User.objects.get(id=user_id)
                listing = Listing(title=title, description=description, starting_bid=starting_bid, current_bid=starting_bid, image_url=image_url, category=category, creator=creator)
                listing.save()
                return HttpResponseRedirect(reverse('index'))
            except IntegrityError as e:
                print(e)
                return HttpResponse('Error')
            
    return render(request, 'auctions/create.html', {
        "form": ListingForm()
    })
    
def listing(request, listing_id):
    user_id = request.session['user_id']
    listing = Listing.objects.get(pk=listing_id)
    comments = Comment.objects.all().filter(listing=listing_id).order_by("-created_at")
    bids = Bid.objects.all().filter(listing=listing_id)
    print(listing.active)
          
    return render(request, 'auctions/listing.html', {
        'item': listing, 
        'bid_form': BidForm(),
        'comments': comments,
        'comment_form': CommentForm(),
        'in_watchlist': in_watchlist(user_id, listing),
        'owner': owner(listing, user_id),
        'bids': len(bids),
        'bidder': bidder(user_id, listing_id),
        'winner': bid_winner(user_id, listing_id),
        'is_active': listing.active
    })

@login_required
def add_comment(request, listing_id):
    user_id = request.session['user_id']
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            
            try:
                listing = Listing.objects.get(pk=listing_id)
                user = User.objects.get(pk=user_id)
                comment = Comment(user=user, listing=listing, content=content)
                comment.save()
                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            except IntegrityError as e:
                print(e)
                return HttpResponse("Couldn't add comment")

@login_required         
def add_watchlist(request, listing_id):
    user_id = request.session['user_id']
    if request.method == "POST":
        try:
            user = User.objects.get(pk=user_id)
            listing = Listing.objects.get(pk=listing_id)
            if listing in user.watchlist.all():
                user.watchlist.remove(listing)   
            else:
                user.watchlist.add(listing)
            user.save()
            return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
        except IntegrityError as e:
            print(e)
            return HttpResponse("Couldn't add listing to watchlist")

@login_required
def watchlist(request):
    user_id = request.session['user_id']
    user = User.objects.get(pk=user_id)
    return render(request, 'auctions/watchlist.html', {
        'watchlist': user.watchlist.all()
    })

@login_required
def add_bid(request, listing_id):
    user_id = request.session['user_id']
    
    if request.method == "POST":
        form = BidForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            bidder = User.objects.get(pk=user_id)
            listing = Listing.objects.get(pk=listing_id)
            
            if amount < listing.current_bid:
                return HttpResponse('Amount is less than current bid')
            
            try:
                listing.current_bid = amount
                bid = Bid(listing=listing, bidder=bidder, amount=amount)
                listing.save()
                bid.save()
                return HttpResponseRedirect(reverse('listing', args=(listing_id,)))
            except IntegrityError as e:
                print(e)
                return HttpResponse('Error placind a bid')
                
         
@login_required   
def close_bid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        listing.active = False
        listing.save()
    return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

def categories(request):
    categories = Category.objects.all()
    
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })

def category_page(request, category):
    category_id = Category.objects.get(name=category).id
    listings = Listing.objects.all().filter(category=category_id, active=True)
    
    return render(request, 'auctions/category_page.html', {
        'listings': listings,
        'category': category
    })