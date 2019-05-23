"""tri_form_presentation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path

from forum import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    path(r'django/1/', views.django_example1),
    path(r'tri_form/1/', views.tri_form_example1),

    path(r'django/1b/', views.DjangoExample1B.as_view()),
    path(r'tri_form/1b/', views.tri_form_example1_b),

    path(r'django/2/', views.DjangoExample2.as_view()),
    path(r'tri_form/2/', views.tri_form_example2),

    path(r'django/3/<int:pk>/', views.DjangoExample3.as_view()),
    path(r'tri_form/3/<int:pk>/', views.tri_form_example3),
]
