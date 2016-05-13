"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin
from manager import views as ManagerViews
from rest_framework.authtoken import views as TokenViews

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', ManagerViews.mainView, name='main'),
    url(r'^register/$', ManagerViews.registrationView, name='register'),
    url(r'^login/', ManagerViews.loginView, name='login'),
    url(r'^logout/', ManagerViews.logoutView, name='logout'),
    url(r'^entry/add/$', ManagerViews.addEntryView, name='addEntry'),
    url(r'^entry/(?P<pk>[a-zA-Z0-9\-]+)/$', ManagerViews.entryDetailsView, name='entryDetails'),
    url(r'^entry/(?P<pk>[a-zA-Z0-9\-]+)/edit/$', ManagerViews.addEntryView, name='editEntry'),
    url(r'^entry/(?P<pk>[a-zA-Z0-9\-]+)/qrgen/$', ManagerViews.generateQrImage, name='generateQr'),
    url(r'^address/$', ManagerViews.addressView, name='address'),
    url(r'^address/(?P<pk>\d+)/$', ManagerViews.addressDetailView, name='addressDetails'),
    url(r'^address/add/$', ManagerViews.addAddressView, name='addAddress'),
    url(r'^address/edit/(?P<pk>\d+)/$', ManagerViews.addAddressView, name='editAddress'),
    url(r'^room/$', ManagerViews.roomView, name='room'),
    url(r'^room/(?P<pk>\d+)/$', ManagerViews.roomDetailsView, name='roomDetails'),
    url(r'^room/add/$', ManagerViews.addRoomView, name='addRoom'),
    url(r'^room/edit/(?P<pk>\d+)/$', ManagerViews.addRoomView, name='editRoom'),
    url(r'^user/$', ManagerViews.userView, name='user'),
    url(r'^user/(?P<pk>\d+)/$', ManagerViews.userDetailsView, name='userDetails'),
    url(r'^user/(?P<pk>\d+)/activate/$', ManagerViews.changeUserActiveStatus, name='userActivate'),
    url(r'^user/(?P<pk>\d+)/rank/$', ManagerViews.changeUserRank, name='userRank'),
    url(r'^user/(?P<pk>\d+)/remove/$', ManagerViews.removeUser, name='userRemove'),
    url(r'^api/entry/$', ManagerViews.apiEntries, name='apiEntries'),
    url(r'^api/entry/(?P<pk>[a-zA-Z0-9\-]+)/$', ManagerViews.apiEntry, name='apiEntry'),
    url(r'^api/room/$', ManagerViews.apiRooms, name='apiRooms'),
    url(r'^api/room/(?P<pk>\d+)/$', ManagerViews.apiRoom, name='apiRoom'),
    url(r'^api/room/(?P<pk>\d+)/entries$', ManagerViews.apiRoomEntries, name='apiRoomEntries'),
    url(r'^api/address/$', ManagerViews.apiAddresses, name='apiAddresses'),
    url(r'^api/address/(?P<pk>\d+)/$', ManagerViews.apiAddress, name='apiAddress'),
    url(r'^api/address/(?P<pk>\d+)/rooms/$', ManagerViews.apiAddressRooms, name='apiAddressRooms'),
    url(r'^api/login/$', TokenViews.obtain_auth_token, name='apiLogin'),    
]

if settings.DEBUG is True:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
