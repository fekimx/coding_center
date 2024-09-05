from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.forms import ModelForm
import json
from django.core.paginator import Paginator
from .models import User, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['post']

def render_with_paginator(request, posts):
    # 1 is the default page
    page_number = request.GET.get('page', 1) 
    # 10 is the number of posts that are displayed on the page
    paginator = Paginator(posts, 10)
    page = paginator.page(page_number)
    # Don't show the post form if the user is not authenticated
    if not request.user.is_authenticated :
        return render(request, "network/index.html", {
            'page': page
        })
    else:
        return render(request, "network/index.html", {
            'page': page,
            "post_form": PostForm()
        })


def index(request):
    posts = Post.objects.all()
    # Order by reverse chronological order
    posts = posts.order_by("-date_time_posted").all()
    return render_with_paginator(request, posts)

# Create the post when the user clicks the Post button and reload the page 
@login_required
def post(request):
    if request.method == "POST":
        text = request.POST["post"]
        Post.objects.create(author=request.user, post=text)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/notification.html", {
            "message": "It is not a POST method.",
        })

def profile(request, user_id):
    user = User.objects.get(id=user_id)
    
    return render(request, "network/profile.html", {
        "profile_user": user
    })

# Get the content of the textarea when the user clicks Save, update the dabase,
# and send a JsonResponse with the new content
@csrf_exempt
def update_post(request, post_id):
    if request.method == "PUT":
        data = json.loads(request.body)
        obj = Post.objects.get(id=post_id)
        obj.post = data.get("new_content", "")
        obj.save()
        return JsonResponse({"content": obj.post}, status=201)

# If Like button is clicked, add or remove the user depending on if he or she already liked the post

@csrf_exempt
def like(request, post_id):
    # Code I'd use if I wasn't doing it in JS
    # if request.method == "POST":
    #     post = Post.objects.get(id=post_id)
    #     if request.user not in post.liker.all():
    #         request.user.liked_posts.add(post)
    #         post.liker.add(request.user)
    #     else:
    #         request.user.liked_posts.remove(post)
    #         post.liker.remove(request.user)
    post = Post.objects.get(id=post_id)
    
    if request.method == "GET":
        if request.user not in post.likers.all():
            post.likers.add(request.user)
        else:
            post.likers.remove(request.user)
        # serialize method returns "likers": [liker.username for liker in self.likers.all()]
        return JsonResponse(post.serialize()) 

# Follow or unfollow the user 
@csrf_exempt
def follow(request, user_id):
    if request.method == "POST":
        person = User.objects.get(id=user_id)
        if person not in request.user.following.all():
            request.user.following.add(person)
            person.followers.add(request.user)
        else:
            request.user.following.remove(person)
            person.followers.remove(request.user)
    return HttpResponseRedirect(reverse("profile", args=(user_id,)))

# This is for the following page
def following(request):
    posts = Post.objects.all()
    posts = posts.order_by("-date_time_posted").all()
    page_number = request.GET.get('page', 1) # 1 is default
    paginator = Paginator(posts, 10)
    page = paginator.page(page_number)
    return render(request, "network/following.html", {
            'page': page
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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
