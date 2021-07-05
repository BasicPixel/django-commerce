from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("save_to_watchlist/<int:listing_id>", views.save_to_watchlist, name="save_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("delete/<int:listing_id>", views.delete, name="delete"),
    path("close/<int:listing_id>", views.close, name="close"),
    path('place_bid/<int:listing_id>', views.place_bid, name='place_bid'),
    path('add_comment/<int:listing_id>', views.add_comment, name='add_comment'),
    path("user/<int:user_id>/listings", views.user_view, name="user"),
    path("user/<int:user_id>/watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category_name>", views.category_view, name="category"),
]
