"""
URL configuration for socialmedia project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

"""
urls.py — API Route Configuration
==================================
Django REST Framework's DefaultRouter auto-generates these routes:

  GET    /api/users/           → UserViewSet.list()
  GET    /api/users/<id>/      → UserViewSet.retrieve()
  GET    /api/users/me/        → UserViewSet.me()       [custom]
  GET    /api/users/<id>/posts/→ UserViewSet.posts()    [custom]
  GET    /api/users/feed/      → UserViewSet.feed()     [custom]
  POST   /api/users/<id>/follow/ → UserViewSet.follow() [custom]

  GET    /api/posts/           → PostViewSet.list()
  POST   /api/posts/           → PostViewSet.create()
  GET    /api/posts/<id>/      → PostViewSet.retrieve()
  DELETE /api/posts/<id>/      → PostViewSet.destroy()
  POST   /api/posts/<id>/like/    → PostViewSet.like()    [custom]
  POST   /api/posts/<id>/comment/ → PostViewSet.comment() [custom]

  POST   /api/register/        → RegisterView
  POST   /api/login/           → LoginView
  POST   /api/token/refresh/   → TokenRefreshView (JWT)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.generic import TemplateView

from core.views import (
    RegisterView, LoginView,
    UserViewSet, PostViewSet,
)

# Router auto-generates CRUD endpoints for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'posts', PostViewSet, basename='post')

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth endpoints
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # All /api/users/ and /api/posts/ routes from the router
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='index.html')),
]

# Serve media files (avatars, post images) during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)