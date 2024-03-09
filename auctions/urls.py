from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("<int:listing_id>", views.listing, name='listing'),
    path("<int:listing_id>/add_comment", views.add_comment, name='add_comment'),
    path('<int:listing_id>/add_watchlist', views.add_watchlist, name='add_watchlist'),
    path('<int:listing_id>/add_bid', views.add_bid, name='add_bid'),
    path('<int:listing_id>/close_bid', views.close_bid, name='close_bid'),
    path('watchlist', views.watchlist, name='watchlist'),
    path('categories', views.categories, name='categories'),
    path('categories/<str:category>', views.category_page, name='category_page')
]
