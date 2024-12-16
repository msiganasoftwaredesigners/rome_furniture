from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.post_list, name='blog'),
    path('posts/<slug:slug>/', views.post_detail, name='post_detail'),
]