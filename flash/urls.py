from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from prode import views

urlpatterns = [
    url(r'^prode/$', views.GoodsList.as_view()),
    url(r'^admin/', admin.site.urls),
]
