from django.conf.urls import patterns, include, url

from cointrax import views


urlpatterns = patterns('',
    url(r'^captcha/', include('captcha.urls')),
    url(r'^$', views.index, name='index'),
    url(r'^address/(\S+)/$', views.address, name='address'),
    url(r'^not-available/$', views.not_available, name='not_available'),
    url(r'^not-in-system/$', views.not_in_system, name='not_in_system'),
    url(r'^forbidden/$', views.forbidden, name='forbidden'),
    url(r'^btcprice/', views.btcprice, name='btcprice'),
    url(r'^btctrans/(\S+)/', views.btctrans, name='btctrans'),
    url(r'^qrcode/', views.qrcode, name='qrcode'),
    url(r'^address-report/', views.address_report, name='address_report'),
    url(r'^registration-report/', views.registration_report, name='registration_report'),
)
