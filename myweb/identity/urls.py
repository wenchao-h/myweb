from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.index),
    path('login/', views.login),
    path('register/',views.register),
    path('activate/', views.userActivate),
    path('changepassword/', views.changePassword),
    path('logout/', views.logout),
]
