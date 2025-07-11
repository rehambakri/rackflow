"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("product/", include("product.urls")),
    path("notification/", include("notification.urls")),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("consumer/", include("consumer.urls")),
    path("provider/", include("provider.urls")),
    path("", include("authentication.urls")),
    path("dashboard/", include("dashboard.urls")),    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
