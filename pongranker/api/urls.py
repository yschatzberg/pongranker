from pongranker.api import views

__author__ = 'yoavschatzberg'

__author__ = 'yoavschatzberg'
from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^player_emails_and_names/$', views.get_player_emails_and_names, name="get_player_emails_and_names"),


    # url(r'^.', views.unknown, name='unknown'),

)