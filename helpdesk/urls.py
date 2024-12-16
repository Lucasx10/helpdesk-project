from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("app.urls")),
]

handler404 = 'app.views.custom_handler404' 