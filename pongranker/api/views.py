__author__ = 'yoavschatzberg'
from django.http import HttpResponse
from django.template import RequestContext

import json
import time
from elo import rate_1vs1

from pongranker.models import Player, Match, MatchGame, DoublesMatch, DoublesTeam
from django.contrib.auth.models import User
from pongranker.api import helper_functions


# Returns the player names and emails, used for building player choice lists.
def get_player_emails_and_names(request):
    player_list = User.objects.order_by('first_name', 'last_name')

    response = []
    for player in player_list:
        if not player.is_superuser:
            response.append(( player.email, player.first_name + " " + player.last_name))

    return HttpResponse(json.dumps(response), content_type="application/json")


# TODO: change this to get_singles_matches and implement get_doubles_matches once DoublesMatch exists.
def get_singles_matches(request):

    response = []

    if request.method == 'GET':
        match_list = Match.objects.order_by("-timestamp")

        max_matches = request.GET.get('max_matches', len(match_list))
        max_matches = int(max_matches)

        for match in match_list[:max_matches]:
            match_json = {}
            match_json[u'player_1'] = match.player_1
            match_json[u'player_2'] = match.player_2
            match_json[u'p1_point_change'] = match.team_1_point_change
            match_json[u'p2_point_change'] = match.team_2_point_change
            match_json[u'p1_wins'] = match.team_1_wins
            match_json[u'p2_wins'] = match.team_2_wins
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


def get_doubles_matches(request):

    response = []

    if request.method == 'GET':
        match_list = DoublesMatch.objects.order_by("-timestamp")

        max_matches = request.GET.get('max_matches', len(match_list))
        max_matches = int(max_matches)

        for match in match_list[:max_matches]:
            match_json = {}
            team_1_name = match.team_1_name
            if not team_1_name:
                team_1_name = helper_functions.get_team_short_name(match.player_1, match.player_3)
            match_json[u'team_1'] = team_1_name

            team_2_name = match.team_2_name
            if not team_2_name:
                team_2_name = helper_functions.get_team_short_name(match.player_2, match.player_4)
            match_json[u'team_2'] = team_2_name

            match_json[u'team_1_point_change'] = match.team_1_point_change
            match_json[u'team_2_point_change'] = match.team_2_point_change
            match_json[u'team_1_wins'] = match.team_1_wins
            match_json[u'team_2_wins'] = match.team_2_wins
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


# This is the new one
def post_match(request):
    if request.method == 'POST':

        team_1_json = json.loads(request.POST['team_1'])
        team_2_json = json.loads(request.POST['team_2'])

        # Get team objects, might be a DoublesTeam, might be a Player
        try:
            team_1 = helper_functions.build_team_object(team_1_json)
            team_2 = helper_functions.build_team_object(team_2_json)
        except ValueError as e:
            return HttpResponse(json.dumps({"error": 1, "message": str(e)}), content_type="application/json")

        # Check which team has priority and swap if necessary.
        try:
            if helper_functions.get_team_full_name(team_2) < helper_functions.get_team_full_name(team_1):
                # flip lists of players so that team 1 is alphabetically superior
                team_1, team_2 = team_2, team_1
                # flip scores so that scores align with players
                team_1_json['scores'], team_2_json['scores'] = team_2_json['scores'], team_1_json['scores']
        except ValueError as e:
            return HttpResponse(json.dumps({"error": 2, "message": str(e)}), content_type="application/json")

        team_1_player_list = helper_functions.get_team_player_list(team_1)
        team_2_player_list = helper_functions.get_team_player_list(team_2)

        # IF either team has more than on player, create a DoublesMatch
        if len(team_1_player_list) == 2 or len(team_2_player_list) == 2:
            match = DoublesMatch(
                player_1=(team_1_player_list[0].user.first_name + " " + team_1_player_list[0].user.last_name),
                player_2=(team_2_player_list[0].user.first_name + " " + team_2_player_list[0].user.last_name)
            )

            # Add second player to the team (if it exists).
            if len(team_1_player_list) == 2:
                match.player_3 = team_1_player_list[1].user.first_name + " " + team_1_player_list[1].user.last_name
            if len(team_2_player_list) == 2:
                match.player_4 = team_2_player_list[1].user.first_name + " " + team_2_player_list[1].user.last_name

            # Add team names if they exist
            if team_1.team_name:
                match.team_1_name = team_1.team_name
            if team_2.team_name:
                match.team_2_name = team_2.team_name
        else:
            # Create Match object
            match = Match(
                player_1=(team_1_player_list[0].user.first_name + " " + team_1_player_list[0].user.last_name),
                player_2=(team_2_player_list[0].user.first_name + " " + team_2_player_list[0].user.last_name)
            )

        match.timestamp = time.time()
        match.full_clean()
        match.save()

        game_list = []
        # for each score pair add a game
        for score in team_1_json['scores']:
            # Create game object
            game = MatchGame(
                score_1=score,
                #get index of score in team_1['scores'] and get the team_2['scores'] item at that same index
                score_2=team_2_json['scores'][team_1_json['scores'].index(score)]
            )

            game.full_clean()
            game.save()
            # Add to game list
            game_list.append(game)

            # Grab old list for point change calculations
            old_ratings = (team_1.elo_ranking, team_2.elo_ranking)

            # update ratings, total wins/losses, and calculate point change from game
            if game.score_1 > game.score_2:
                # Calculate new ranking
                new_ratings = rate_1vs1(team_1.elo_ranking, team_2.elo_ranking)
                team_1.elo_ranking = round(new_ratings[0])
                team_2.elo_ranking = round(new_ratings[1])

                #wins/losses for player and match
                match.team_1_wins += 1

                # match point change
                match.team_1_point_change = team_1.elo_ranking - old_ratings[0]
                match.team_2_point_change = team_2.elo_ranking - old_ratings[1]
            else:
                new_ratings = rate_1vs1(team_2.elo_ranking, team_1.elo_ranking)
                team_2.elo_ranking = round(new_ratings[0])
                team_1.elo_ranking = round(new_ratings[1])

                match.team_2_wins += 1
                match.team_1_point_change = team_1.elo_ranking - old_ratings[1]
                match.team_2_point_change = team_2.elo_ranking - old_ratings[0]

        for g in game_list:
            match.games.add(g)

        match.save()

        # Adding a win based on who won the match
        if match.team_1_wins > match.team_2_wins:
            team_1.total_wins += 1
            team_2.total_losses += 1
        else:
            team_2.total_wins += 1
            team_1.total_losses += 1

        # If team is 1 player, only add it to them, otherwise, add to team object
        # TODO: This will fail if one of the teams is a Doubles Team and the other is a Player
        for team in [team_1, team_2]:
            team.matches.add(match)
            team.save()

    return HttpResponse(json.dumps({"error": 0, "message": "OK"}), content_type="application/json")


# TODO: Create get_teams_ranked
def get_players_ranked(request):

    if request.method == 'GET':
        response_json = {}
        player_list = Player.objects.order_by('-elo_ranking','-total_wins')

        max_matches = request.GET.get('max_results', len(player_list))
        max_matches = int(max_matches)

        response_json = []
        for player in player_list[:max_matches]:
            if (player.total_wins + player.total_losses) > 0:
                player_json = {}
                player_json['name'] = player.user.first_name + " " + player.user.last_name
                player_json['ranking'] = player.elo_ranking
                player_json['wins'] = player.total_wins
                player_json['losses'] = player.total_losses

                response_json.append(player_json)

        return HttpResponse(json.dumps(response_json), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"error": 10, "message": "Must use GET request to access this site."}),
            content_type="application/json"
        )

def get_teams_ranked(request):

    if request.method == 'GET':
        response_json = {}
        team_list = DoublesTeam.objects.order_by('-elo_ranking','-total_wins')
        max_matches = request.GET.get('max_results', len(team_list))
        max_matches = int(max_matches)

        response_json = []
        for team in team_list[:max_matches]:
            if (team.total_wins + team.total_losses) > 0:
                team_json = {}
                name = team.team_name
                if not name:
                    player_name_list = []
                    for player in team.players.all():
                        player_name_list.append(player.user.first_name)

                    name = " and ".join(player_name_list)

                team_json['name'] = name
                team_json['ranking'] = team.elo_ranking
                team_json['wins'] = team.total_wins
                team_json['losses'] = team.total_losses

                response_json.append(team_json)

        return HttpResponse(json.dumps(response_json), content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"error": 10, "message": "Must use GET request to access this site."}),
            content_type="application/json"
        )
