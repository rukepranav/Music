from django.conf.urls import url
from . import views

app_name = 'Music'

urlpatterns = [
    # /music/
    url(r'^$', views.index, name='index'),
    # /music/71/
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    # /music/71/favorite
    url(r'^(?P<album_id>[0-9]+)/favorite/$', views.favorite_album, name='album-favorite'),
    #register
    url(r'^register/$', views.UserFormView.as_view(), name='register'),
    #Add album
    #url(r'^album/add/$', views.AlbumCreate.as_view(), name='album-add'),
    url(r'^album/add/$', views.create_album, name='album-add'),
    #Edit Album
    url(r'^album/(?P<pk>[0-9]+)/$', views.AlbumUpdate.as_view(), name='album-update'),
    #Delete Album
    url(r'^album/(?P<album_id>[0-9]+)/delete/$', views.delete_album, name='album-delete'),

    url(r'^log_in/$', views.login_user, name='login_user'),

    url(r'^logout_user/$', views.logout_user, name='logout_user'),

    #favorite song
    url(r'^(?P<album_id>[0-9]+)/favorite_song/(?P<song_id>[0-9]+)/$', views.favorite_song, name='song-favorite'),

    url(r'^(?P<album_id>[0-9]+)/delete_song/(?P<song_id>[0-9]+)/$', views.delete_song, name='delete_song'),

    url(r'^(?P<album_id>[0-9]+)/create_song/$', views.create_song, name='create_song'),

    url(r'^songs/(?P<filter_by>[a-zA_Z]+)/$', views.songs, name='songs')
]
