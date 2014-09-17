__author__ = 'yoavschatzberg'
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.db import IntegrityError
from django.template import RequestContext, loader

import json
from pongranker.models import Player, Game
from django.contrib.auth.models import User


def get_player_emails_and_names(request):
    player_list = User.objects.order_by('first_name', 'last_name')

    response = {}
    for player in player_list:
      if not player.is_superuser:
        response[player.email] = player.first_name + " " + player.last_name

    return HttpResponse(json.dumps(response), content_type="application/json")