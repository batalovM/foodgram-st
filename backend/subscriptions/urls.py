from django.urls import path
from . import views

urlpatterns = [
    path("users/subscriptions/", views.subscriptions_list, name="subscription-list"),
]
