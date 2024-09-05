from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # People you follow: following 
    # People that follows you: followers
    following = models.ManyToManyField("User", related_name="followers")
    # user.likes is the posts that the user likes
    # post.likers is the list of the users that like the post
    likes = models.ManyToManyField("Post", related_name="likers")

    def serialize(self):
        return {
            "likes": [post.post for post in self.likes.all()]
        }

class Post(models.Model):
    author = models.ForeignKey("User", on_delete=models.CASCADE, related_name='posts')
    post = models.TextField(blank=False, verbose_name="")
    date_time_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.post} posted on {self.date_time_posted}"
    
    def serialize(self):
        return {
            "likers": [liker.username for liker in self.likers.all()],
        }
