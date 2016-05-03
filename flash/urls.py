from django.conf.urls import url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from prode import views

urlpatterns = [
    url(r'^prode/$', views.GoodsList.as_view()),
    url(r'^prode/single/$', views.Single.as_view()),
    url(r'^prode/index/$', views.Index.as_view()),
    url(r'^prode/history/$', views.History.as_view()),
    url(r'^admin/', admin.site.urls),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
