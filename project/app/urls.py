from django.contrib import admin
from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.start, name="start"),
    path('generate/', views.generate, name="generate"),
    path('registrations/', views.view_registrations, name="view_registrations"),

    path('register/<int:sid>', views.register, name="register"),
    path('unregister/<int:sid>', views.unregister, name="unregister"),


    path('login/',views.signin, name='signin'),
    path('logout/',views.signout, name='signout'),
  ]
