__author__ = 'yoavschatzberg'

from pongranker.models import Player, DoublesTeam
from django.contrib.auth.models import User

def build_team_object(team_json):

    if len(team_json['players']) > 0:
        player_1 = Player.objects.get(user=User.objects.get(username=team_json['players'][0]))
    else:
        # This is an error case, raise error
        raise(ValueError, "No players in one of the teams")

    if len(team_json['players']) == 1:
        team = player_1
    elif len(team_json['players']) == 2:
        # Get player 2
        player_2 = Player.objects.get(user=User.objects.get(username=team_json['players'][1]))

        # Get the team object, or false
        team = get_team_by_players(player_1, player_2)

        if team is False:
            # Create new team
            team = DoublesTeam()
            team.save()
            team.players.add(player_1)
            team.players.add(player_2)
            team.save()

    else:
        raise ValueError("Too many players on a team: " + len(team_json['players']))

    return team

def get_team_full_name(team):
    # Check the type of the team object
    if isinstance(team, DoublesTeam):
        # Get players in team
        playername = []
        for player in team.players.all():
            playername.append(player.user.first_name + player.user.last_name)

        if playername[1] < playername[0]:
            # flip players for alphabeticalness
            playername[0],playername[1] = playername[1],playername[0]

        # Build full Team Name
        return playername[0] + playername[1]
    elif isinstance(team, Player):
        # Return the first name + last name
        return team.user.first_name + team.user.last_name
    else:
        raise ValueError("get_team_full_name: Team object is not of a valid type: " + type(team))

# Returns a list of players (either 1 or 2)
def get_team_player_list(team):
    # Check the type of the team object
    if isinstance(team, DoublesTeam):
        return team.players.all()
    elif isinstance(team, Player):
        # return a single object in a list (so that we can use it same as a team list.
        return [team]
    else:
        raise ValueError("get_team_player_list: Team object is not of a valid type: " + type(team))

def get_team_by_players(player_1, player_2):
    player_1_teams = player_1.doublesteam_set.all()
    player_2_teams = player_2.doublesteam_set.all()

    for team in player_1_teams:
        # If we find it, return the object
        if team in player_2_teams:
            return team
    # Otherwise return False
    return False


# Returns either the team name or first name of each player separated by "and"
def get_team_short_name(player_1, player_2):
    first_names = []
    for player in [player_1, player_2]:
        try:
            first_names.append(player.split()[0])
        except:
            raise ValueError(player_1 + " " + player_2)

    name = " and ".join(first_names)

    return name
