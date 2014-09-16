__author__ = 'yoavschatzberg'
from django.conf.urls import patterns, url

from pongranker import views

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^players/$', views.players, name='players'),
    url(r'^leaderboard/', views.leaderboard, name='leaderboard'),
    url(r'^register/$', views.register, name='register'), # TODO: add handling for already logged in users
    url(r'^login/$', views.sign_in, name='sign_in'),
    url(r'^logout/$', views.sign_out, name='sign_out'),
    url(r'^add_game/$', views.add_game, name='add_game'),
    url(r'^player_emails_and_names/$', views.get_player_emails_and_names, name="get_player_emails_and_names"),
    url(r'^players/(?P<player_uname>\D+)/$', views.player_detail, name='player_detail'), # TODO: buildout

    # url(r'^.', views.unknown, name='unknown'),

)