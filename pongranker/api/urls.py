from pongranker.api import views


__author__ = 'yoavschatzberg'
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^player_emails_and_names/$', views.get_player_emails_and_names, name="get_player_emails_and_names"),
    url(r'^players_ranked/$', views.get_players_ranked, name="get_players_ranked"),
    url(r'^teams_ranked/$', views.get_teams_ranked, name="get_teams_ranked"),
    url(r'^singles_matches/$', views.get_singles_matches, name="get_singles_matches"),
    url(r'^doubles_matches/$', views.get_doubles_matches, name="get_doubles_matches"),
    url(r'^post_match/$', views.post_match, name="post_match"),


    # url(r'^.', views.unknown, name='unknown'),

)