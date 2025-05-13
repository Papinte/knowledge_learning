from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.shortcuts import render

urlpatterns = [
    path('', lambda request: render(request, 'home.html'), name='home'),
    path('admin/', admin.site.urls),
    path('', include('learning.urls')),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
]