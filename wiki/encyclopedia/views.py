from django.shortcuts import render
import markdown
import random
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse

global_title = ""
global_content = ""


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# It checks if title exists by calling util's get_entry function.
# If it exists, it saves the markdown as a html and loads that html.
# If it doesn't exist, it renders error.html page with a custom message.
def entry(request, title):
    # global variables were created to access the current page's title and content
    # inside the edit and save functions.
    global global_content, global_title
    if util.get_entry(title) != None:
        html = markdown.markdown(util.get_entry(title))
        global_title = title
        global_content = util.get_entry(title)
        return render(request, "encyclopedia/entry.html", {
            "html": html
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error_msg": "Oops, page not found"
        })

# It gets the query (q) when the user presses enter after typing in the search field
# and loads the page if the page exists. If not, it checks if it appears in any of the entry titles. 
# If it does, it adds that entry to results list and renders the page with results.
def query(request):
    q = request.GET.get('q')
    if util.get_entry(q) != None:
        return HttpResponseRedirect(reverse('entry', args=(q,)))
    else:
        results = []
        for entry in util.list_entries():
            if q in entry:
                results.append(entry)
        return render(request, 'encyclopedia/search.html', {
            "results": results
        })

# It simply renders create.html page which has the title, content text fields and the submit button.
def create(request):
    return render(request, "encyclopedia/create.html")

# Its purpose is to add a new page if it doesn't exist. If it does, it displays a warning msg.
def create_page(request):
    title = request.POST.get('title', '')
    content = request.POST.get('content', '')
    for e in util.list_entries():
        #if exists, render the error.html page with a custom message.
        if e == title:
            return render(request, "encyclopedia/error.html", {
                "error_msg": "Oopsie, page already exists."
            })
    #if it doesn't exist, add and redirect to that page
    util.save_entry(title, content)
    return HttpResponseRedirect(reverse('entry', args=(title,)))

# It picks a random page from util's list_entries and redirects to that page.
def random_page(request):
    r = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse('entry', args=(r,)))

# It renders edit.html which has the textarea called content and Save button.
# It preloads the value of the textarea by calling the global_content variable 
# which has the value assigned in the entry function.
def edit(request):
    return render(request, "encyclopedia/edit.html", {
        "markdown_content": global_content
    })

# It saves the changes and redirects to that page.
def save(request):
    new_content = request.POST.get('content',)
    util.save_entry(global_title, new_content)
    return HttpResponseRedirect(reverse('entry', args=(global_title,)))
