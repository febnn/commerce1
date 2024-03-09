from .models import *

def in_watchlist(user_id, listing):
    if user_id:
        watchlist = User.objects.get(pk=user_id).watchlist.all()
        if listing in watchlist:
            return True
        else:
            return False
    else:
        return False
    
def owner(listing, user_id):
    if listing.creator.id == user_id:
        return True
    else:
        return False
    
def bidder(user_id, listing_id):
    bids = Bid.objects.all().filter(listing=listing_id)
    
    if bids:
        return user_id == bids.last().bidder.id
    else:
        return False
    
def bid_winner(user_id, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.all().filter(listing=listing_id)
    
    if bids:
        if not listing.active:
            if user_id == bids.last().bidder.id:
                return "You have won an auction"
            else:
                return f"{bids.last().bidder} has won an auction"
    
    
    
    
    