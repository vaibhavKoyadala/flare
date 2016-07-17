from django.conf.urls import url
import views, api
urlpatterns = [
    url(r'^$', view=views.index, name='index'),
    url(r'^join$', view=views.join_flare, name='join'),
    url(r'^create$',view=views.create_flare, name='create'),
    url(r'^flare$', view=views.flare, name='flare'),
    url(r'^logout', view=views.logout, name='logout'),

    url(r'^api/messages$', view=api.fetch_messages),
    url(r'^api/files$', view=api.fetch_files),
    url(r'^api/send$', view=api.send_message),
    url(r'^api/upload$', view=api.upload),
    url(r'^api/resource/(?P<type>.+)/(?P<id>[0-9]+)/(?P<title>.+)$', view=api.resource),
    url(r'^api/account$', view=api.account, name='account')
]