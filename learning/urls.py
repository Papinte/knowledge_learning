from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('logout/', views.user_logout, name='logout'),
    path('buy-cursus/<int:cursus_id>/', views.buy_cursus, name='buy_cursus'),
    path('buy-lesson/<int:lesson_id>/', views.buy_lesson, name='buy_lesson'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
]