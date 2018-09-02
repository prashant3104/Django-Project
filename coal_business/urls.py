"""coal_business URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from coal.views import *

urlpatterns = [
    url(r'^$', default, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', login, name='login'),
    url(r'^register/$', register, name='register'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^dashboard/$',dashboard, name='dashboard'),
    url(r'^warehouse/$',warehouse, name='warehouse'),
    url(r'^offer/$',offer, name='offer'),
    url(r'^history/$',history, name='history'),
    url(r'^admin_dashboard/$', admin_dashboard, name='admin_dashboard'),
    url(r'^update/$',update, name='update'),
    url(r'^profile/$',profile, name='profile'),
    url(r'^edit/$',edit, name='edit'),
]
