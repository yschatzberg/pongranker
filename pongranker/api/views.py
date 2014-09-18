__author__ = 'yoavschatzberg'
from django.http import HttpResponse

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

# currently gets 5 games.
def get_games(request):

    max_games = 5
    param = request.GET.get('max_games')
    if param:
      max_games = int(max_games)



    game_list = Game.objects.order_by("-game_date")[:max_games]

    response = []
    for game in game_list:
      game_json = {}
      game_json[u'player_1'] = game.player_1
      game_json[u'score_1'] =  game.score_1

      game_json[u'player_2'] = game.player_2
      game_json[u'score_2'] = game.score_2
      game_json[u'game_date'] = str(game.game_date)
      response.append(game_json)
    return HttpResponse(json.dumps(response), content_type="application/json")

