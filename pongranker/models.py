from django.db import models
from django.contrib.auth.models import User
import time
class Game(models.Model):

    # first player, alphabetically.  i.e. arzav jain before yoav schatzberg
    # this is constructed by concatenating user.first_name user.last_name with a space
    player_1 = models.CharField(max_length=100)

    score_1    = models.IntegerField()

    player_2 = models.CharField(max_length=100)

    score_2    = models.IntegerField()

    game_date  = models.DateField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return "\nPlayer 1: " + self.player_1 + \
                "\nPlayer 2: " + self.player_2 + \
                "\nScore 1: " + str(self.score_1) + \
                "\nScore 2: " + str(self.score_2) + \
                "\nGame Date: " + str(self.game_date) + \
               "\n"
class MatchGame(models.Model):
      # score for player 1 in the Match
      score_1    = models.IntegerField()
      #score for player 2 in the Match
      score_2    = models.IntegerField()

class Match(models.Model):
    # first player, alphabetically.  i.e. arzav jain before yoav schatzberg
    # this is constructed by concatenating user.first_name user.last_name[0] with a space
    player_1 = models.CharField(max_length=100)

    player_2 = models.CharField(max_length=100)

    p1_wins = models.IntegerField(default=0)
    p2_wins = models.IntegerField(default=0)

    games = models.ManyToManyField(MatchGame)

    timestamp = models.BigIntegerField(default=int(round(time.time())))

# A single player
class Player(models.Model):
    # the users login
    user = models.OneToOneField(User)


    # total number of singles wins
    total_singles_wins      = models.IntegerField(default=0)

    # total number of singles losses.
    total_singles_losses    = models.IntegerField(default=0)

    # players Singles Ranking.
    elo_singles_ranking         = models.IntegerField(default=1200)

    games = models.ManyToManyField(Game)

    def __unicode__(self):
        return "\nEmail: " + self.user.email + \
               "\nName: " + self.user.first_name + " " + self.user.last_name + \
               "\nRanking: " + str(self.elo_singles_ranking) + \
               "\nTotal Wins: " + str(self.total_singles_wins) + \
               "\nTotal Losses: " + str(self.total_singles_losses) + "\n"


class SinglesMatchup(models.Model):
    # Hash of the players names in the form word1Word2Word3_word1Word2Word3 in alphabetical order of names
    # (e.g. benAsherKlein_yoavSchatzberg)
    name_hash       = models.CharField(max_length=100, primary_key=True)

    # the list of players involved in this matchup.  always added alphabetically
    players         = models.ManyToManyField(Player)

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
    name    = models.CharField(max_length=50, primary_key=True)
    wins    = models.IntegerField(default=0)

    def __unicode__(self):
        return  "\nMatchup: " + self.matchup.name_hash + \
                "\nName: " + self.name + \
                "\nWins: " + str(self.wins)

