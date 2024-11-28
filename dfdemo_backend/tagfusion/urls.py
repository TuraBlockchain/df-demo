"""tagfusion URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path

from tagfusion import settings
from tags.views import upchain
from django.conf.urls.static import static
urlpatterns = [
    path('tagfusion/api/get_nft_data/', upchain.get_nft_data),
    path('tagfusion/api/create_up_chain_data/', upchain.create_up_chain_data),
    path('tagfusion/api/get_chain_introduction/', upchain.get_chain_introduction)

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
