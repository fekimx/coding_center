from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE

categories = (
    ('General',),
    ('Electronics & Media',), 
    ('Home & Garden',), 
    ('Clothing & Shoes',), 
    ('Baby & Kids',), 
    ('Vehicles',), 
    ('Toys & Games',),
    ('Sports & Outdoors',),
    ('Health & Beauty',),
    ('Office Supplies',)
)

class User(AbstractUser):
    watchlist = models.ManyToManyField("AuctionListing", related_name="watchers")
    def __str__(self):
        return f"Name: {self.first_name} {self.last_name}."

class AuctionListing(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024)
    #It goes through categories, allows user to choose no category, selects the first one by default.
    category = models.CharField(max_length=32, 
        choices=[(categories[x][0], categories[x][0]) for x in range(0,len(categories))], 
        default=categories[0][0],
        blank=True)
    image = models.URLField(blank=True)
    starting_price = models.IntegerField()
    status = models.BooleanField(default=True) #active or not
    date_posted = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="owner_listings")
    winner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="winner_listings")

    #Returns the current price of the item which is the max of all the bids.
    #Returns the starting price if there is no bid yet.
    def getCurrentPrice(self):
        if len(self.bids.all()) != 0: #bids is the related_name
            return max([bid.amount for bid in self.bids.all()])
        else: 
            return self.starting_price

    def __str__(self):
        return f"Title: {self.title} Category: {self.category} Description: {self.description}"

class Bid(models.Model):
    listing = models.ForeignKey("AuctionListing", on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey("User", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.amount}"

class Comment(models.Model):
    listing = models.ForeignKey("AuctionListing", on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name='commenters')
    comment = models.TextField()
    date_time_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Posted on {self.date_time_posted} by {self.author}" 
