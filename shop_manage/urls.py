"""shop_manage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
import xadmin
from django.contrib import admin
from django.urls import path, re_path, include
from django.views.static import serve

from shop_manage.settings import STATIC_ROOT

handler404 = "ShopSystem.views.page_not_found"

handler400 = "ShopSystem.views.bad_request"

handler500 = "ShopSystem.views.page_error"

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    path('xadmin/', xadmin.site.urls),
    re_path('static/(?P<path>.*)$', serve, {'document_root': STATIC_ROOT}),


    path('', include('ShopSystem.urls', namespace='ShopApp')),
]
