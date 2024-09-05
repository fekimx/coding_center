from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("listing/<int:item_id>/", views.listing, name="listing"),
    path("watchlist/<int:item_id>/", views.watchlist, name="watchlist"),
    path("mywatchlist/", views.viewwatchlist, name="viewwatchlist"),
    path("createlisting/", views.createlisting, name="createlisting"),
    path("create/", views.create, name="create"),
    path("category/<str:category>/", views.category, name="category"),
    path("comment/<int:item_id>/", views.comment, name="comment"),
    path("bid/<int:item_id>/", views.bid, name="bid"),
    path("close/<int:item_id>/", views.close, name="close")
]
#The code below is added to be able to display images
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
