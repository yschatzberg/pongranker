__author__ = 'yoavschatzberg'
from django.http import HttpResponse
from django.template import RequestContext

import json, time
from elo import rate_1vs1

from pongranker.models import Player, Match, MatchGame
from django.contrib.auth.models import User


def get_player_emails_and_names(request):
    player_list = User.objects.order_by('first_name', 'last_name')

    response = {}
    for player in player_list:
      if not player.is_superuser:
        response[player.email] = player.first_name + " " + player.last_name

    return HttpResponse(json.dumps(response), content_type="application/json")

def get_matches(request):

    context = RequestContext(request)
    max = 100
    response = []

    if request.method == 'GET':
      match_list = Match.objects.order_by("-timestamp")

      max = request.GET.get('max_matches',len(match_list))
      max = int(max)


      for match in match_list[:max]:
        match_json = {}
        match_json[u'player_1'] = match.player_1
        match_json[u'player_2'] = match.player_2
        match_json[u'p1_point_change'] = match.p1_point_change
        match_json[u'p2_point_change'] = match.p2_point_change
        match_json[u'p1_wins'] = match.p1_wins
        match_json[u'p2_wins'] = match.p2_wins
        match_json[u'timestamp'] = match.timestamp

        games_json = []

        for game in match.games.all():
          game_json = {}
          game_json[u'score_1'] = game.score_1
          game_json[u'score_2'] = game.score_2

          games_json.append(game_json)

        match_json[u'games'] = games_json

        response.append(match_json)

    return HttpResponse(json.dumps(response), content_type="application/json")

def post_match(request):

    if request.method == 'POST':

      team_1 = json.loads(request.POST['team_1'])
      team_2 = json.loads(request.POST['team_2'])

      team_1_players = []
      team_2_players = []

      # get player objects [Player_object, player_object]
      for player in team_1['players']:
        team_1_players.append(Player.objects.get(user=User.objects.get(username=player)))
      for player in team_2['players']:
        team_2_players.append(Player.objects.get(user=User.objects.get(username=player)))

      # sort the player lists by Player name (first + last)
      for team in [team_1_players,team_2_players]:
        team.sort(key=lambda x: (x.user.last_name,x.user.first_name))


      # which team is inserted as player 1?
      # generate full team name (for comparison)
      team_1_full_name = ""
      for player in team_1_players:
        team_1_full_name += (player.user.first_name + player.user.last_name)

      team_2_full_name = ""
      for player in team_2_players:
        team_2_full_name += (player.user.first_name + player.user.last_name)

      # if team 2 has a higher priority name
      if team_2_full_name < team_1_full_name:
        # flip lists of players so that team 1 is alphabetically superior
        team_1_players,team_2_players = team_2_players,team_1_players
        # flip scores so that scores align with players
        team_1['scores'],team_2['scores'] = team_2['scores'],team_1['scores']
      # scores are stored in team_1['scores']/team_2['scores']

      # TODO: make this work for 2 v 2
      match = Match(player_1=(team_1_players[0].user.first_name + " " +team_1_players[0].user.last_name),
                    player_2=(team_2_players[0].user.first_name + " " +team_2_players[0].user.last_name))
      match.timestamp = time.time()
      match.full_clean()
      match.save()

      game_list = []
      for score in team_1['scores']:
        game = MatchGame(score_1=score,
                         #get index of score in team_1['scores'] and get the team_2['scores'] item at that same index
                         score_2=team_2['scores'][team_1['scores'].index(score)])

        game.full_clean()
        game.save()
        game_list.append(game)

        old_ratings = (team_1_players[0].elo_singles_ranking, team_2_players[0].elo_singles_ranking)

        # update ratings, total wins/losses, and calculate point change from game
        if game.score_1 > game.score_2:
          # Rankings
          new_ratings = rate_1vs1(team_1_players[0].elo_singles_ranking, team_2_players[0].elo_singles_ranking)
          team_1_players[0].elo_singles_ranking = round(new_ratings[0])
          team_2_players[0].elo_singles_ranking = round(new_ratings[1])

          #wins/losses for player and match
          match.p1_wins += 1

          # match point change
          match.p1_point_change += team_1_players[0].elo_singles_ranking - old_ratings[0]
          match.p2_point_change += team_2_players[0].elo_singles_ranking - old_ratings[1]
        else:
          new_ratings = rate_1vs1(team_2_players[0].elo_singles_ranking, team_1_players[0].elo_singles_ranking)
          team_2_players[0].elo_singles_ranking = round(new_ratings[0])
          team_1_players[0].elo_singles_ranking = round(new_ratings[1])

          match.p2_wins += 1
          match.p1_point_change = team_1_players[0].elo_singles_ranking - old_ratings[1]
          match.p2_point_change = team_2_players[0].elo_singles_ranking - old_ratings[0]

      for g in game_list:
        match.games.add(g)

      match.save()

      # Adding a win based on who won the match
      if match.p1_wins > match.p2_wins:
          team_1_players[0].total_singles_wins += 1
          team_2_players[0].total_singles_losses += 1
      else:
          team_2_players[0].total_singles_wins += 1
          team_1_players[0].total_singles_losses += 1

      for team_players in [team_1_players, team_2_players]:
        for player in team_players:
          player.matches.add(match)
          player.save()




    return HttpResponse(json.dumps({"error": 0, "message": "OK"}), content_type="application/json")


def get_players_ranked(request):

    if request.method == 'GET':
      response_json = {}
      player_list = Player.objects.order_by('-elo_singles_ranking','-total_singles_wins')

      max = request.GET.get('max_results', len(player_list))
      max = int(max)

      response_json = []
      for player in player_list[:max]:
        if (player.total_singles_wins + player.total_singles_losses) > 1:
          player_json = {}
          player_json['name'] = player.user.first_name + " " + player.user.last_name
          player_json['ranking'] = player.elo_singles_ranking
          player_json['wins'] = player.total_singles_wins
          player_json['losses'] = player.total_singles_losses

          response_json.append(player_json)

      return HttpResponse(json.dumps(response_json), content_type="application/json")
    else:
      return HttpResponse(json.dumps({"error": 10, "message": "Must use GET request to access this site."}), content_type="application/json")
