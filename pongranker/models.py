from django.db import models
from django.contrib.auth.models import User
import time
import datetime


class MatchGame(models.Model):
    # score for player 1 in the Match
    score_1 = models.IntegerField()
    #score for player 2 in the Match
    score_2 = models.IntegerField()

    def __unicode__(self):
        return "\nTeam 1 Score: " + str(self.score_1) + \
               "\nTeam 2 Score: " + str(self.score_2)

class Match(models.Model):
    # Player name of player in Team 1
    player_1 = models.CharField(max_length=100)

    # Player Name of Player in team 2
    player_2 = models.CharField(max_length=100)

    # Number of points added or subtracted from team 1's ELO
    team_1_point_change = models.IntegerField(default=0)
    # Number of points added or subtracted from team 2's ELO
    team_2_point_change = models.IntegerField(default=0)
    # Number of wins Team 1 had this match
    team_1_wins = models.IntegerField(default=0)
    # Number of wins Team 2 had this match
    team_2_wins = models.IntegerField(default=0)

    # A list of games that occurred during this match.
    games = models.ManyToManyField(MatchGame)

    # Time of match
    timestamp = models.BigIntegerField(default=0)

    def __unicode__(self):
        output = "\nTeam 1: " + self.player_1 + \
                 "\nTeam 1 Point Change: " + str(self.team_1_point_change) + \
                 "\nTeam 2 Point Change: " + str(self.team_2_point_change) + \
                 "\nTeam 2: " + self.player_2 + \
                 "\nTeam 1 Wins: " + str(self.team_1_wins) + \
                 "\nTeam 2 Wins: " + str(self.team_2_wins) + \
                 "\nMatch Date: " + datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')


class DoublesMatch(models.Model):
    # first player in team 1, alphabetically.  i.e. arzav jain before yoav schatzberg
    player_1 = models.CharField(max_length=100)
    # second player in team 1
    player_3 = models.CharField(max_length=100, default='', blank=True)

    # first player in team 2, alphabetically.  i.e. arzav jain before yoav schatzberg
    player_2 = models.CharField(max_length=100)
    # second player in team 1
    player_4 = models.CharField(max_length=100, default='', blank=True)

    # Number of points added or subtracted from team 1's ELO
    team_1_point_change = models.IntegerField(default=0)
    # Number of points added or subtracted from team 2's ELO
    team_2_point_change = models.IntegerField(default=0)
    # Number of wins Team 1 had this match
    team_1_wins = models.IntegerField(default=0)
    # Number of wins Team 2 had this match
    team_2_wins = models.IntegerField(default=0)

    # A list of games that occurred during this match.
    games = models.ManyToManyField(MatchGame)

    # Time of match
    timestamp = models.BigIntegerField(default=0)

    def __unicode__(self):
        output = "\nTeam 1: " + self.player_1 + " " + self.player_3 + \
                 "\nTeam 1 Point Change: " + str(self.team_1_point_change) + \
                 "\nTeam 2 Point Change: " + str(self.team_2_point_change) + \
                 "\nTeam 2: " + self.player_2 + " " + self.player_4 + \
                 "\nTeam 1 Wins: " + str(self.team_1_wins) + \
                 "\nTeam 2 Wins: " + str(self.team_2_wins) + \
                 "\nMatch Date: " + datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')
        i = 1
        for game in self.games.all():
            output += "\nGame " + str(i) + game.__unicode__()
            i += 1

        return output


# A single player
class Player(models.Model):
    # the users login
    user = models.OneToOneField(User)

    # total number of singles wins
    total_wins = models.IntegerField(default=0)

    # total number of singles losses.
    total_losses = models.IntegerField(default=0)

    # players Singles Ranking.
    elo_ranking = models.IntegerField(default=1200)

    # a list of this players Singles Matches
    matches = models.ManyToManyField(Match)

    # A list of this players doubles matches (i.e. 2 v 1's, this is the 1)
    doubles_matches = models.ManyToManyField(DoublesMatch)

    def __unicode__(self):
        return "\nEmail: " + self.user.email + \
               "\nName: " + self.user.first_name + " " + self.user.last_name + \
               "\nRanking: " + str(self.elo_ranking) + \
               "\nTotal Wins: " + str(self.total_wins) + \
               "\nTotal Losses: " + str(self.total_losses) + "\n"


# Team object, This is used for doubles and singles
class DoublesTeam(models.Model):

    # first player, alphabetically.  i.e. arzav jain before yoav schatzberg
    players = models.ManyToManyField(Player)

    # Total wins for this team
    total_wins = models.IntegerField(default=0)

    # Total Losses for this team
    total_losses = models.IntegerField(default=0)

    # Teams Doubles Ranking.
    elo_ranking = models.IntegerField(default=1200)

    # The team name.
    team_name = models.CharField(max_length=100, default="")

    #matches for this team
    matches = models.ManyToManyField(DoublesMatch)

    def __unicode__(self):
        output = "\nTeam Name: " + self.team_name + \
                 "\nPlayers: "

        for player in self.players.all():
            output += "\n  " + player.user.first_name + " " + player.user.last_name

        output += "\nRanking: " + str(self.elo_ranking) + \
                  "\nTotal Wins: " + str(self.total_wins) + \
                  "\nTotal Losses: " + str(self.total_losses) + "\n"
        return output


class SinglesMatchup(models.Model):
    # Hash of the players names in the form word1Word2Word3_word1Word2Word3 in alphabetical order of names
    # (e.g. benAsherKlein_yoavSchatzberg)
    name_hash = models.CharField(max_length=100, primary_key=True)

    # the list of players involved in this matchup.  always added alphabetically
    players = models.ManyToManyField(Player)

    def __unicode__(self):
        output = "\nName Hash: " + self.name_hash

        for player in self.players.all():
            # get player info
            output += "\nName: " + player.name
            output += "\nOverall Ranking: " + str(player.elo_singles_ranking)

            # find the right SinglesMatchupScore object
            scoreObj = self.singlesmatchupscore_set.get(name=player.name)
            output += "\nWins: " + str(scoreObj.wins) + "\n"

        return output


class SinglesMatchupScore(models.Model):

    matchup = models.ForeignKey(SinglesMatchup)
    name = models.CharField(max_length=50, primary_key=True)
    wins = models.IntegerField(default=0)

    def __unicode__(self):
        return "\nMatchup: " + self.matchup.name_hash + \
               "\nName: " + self.name + \
               "\nWins: " + str(self.wins)

