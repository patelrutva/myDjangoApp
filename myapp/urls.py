"""mysiteF19 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import include
from django.contrib import admin
from django.urls import path
from django.conf.urls import *
from myapp import views

app_name = 'myapp'

urlpatterns = [
    path(r'about/', views.about, name='about_page'),
    path(r'<int:book_id>/', views.detail, name='detail'),
    path(r'', views.index, name='index'),
    path(r'findbooks/', views.findbooks, name='findbooks'),
    path(r'place_order/', views.place_order, name='place_order'),
    path(r'review/', views.review, name='review'),
    path(r'login/', views.user_login, name='login'),
    path(r'logout/', views.user_logout, name='logout'),
    path(r'chk_reviews/<int:book_id>', views.chk_reviews, name='chk_reviews'),
    # path(r'cookie', views.test_cookie, name='cookie')
]
