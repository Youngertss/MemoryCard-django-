from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include('game.urls')),
    path("captcha/", include('captcha.urls')),
    path('login/', include('users.urls')),
    path('logout/', include('users.urls')),
    path('registering/', include('users.urls')),
]

# from django.conf.urls.static import static
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)