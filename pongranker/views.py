from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.db import IntegrityError
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout
from elo import rate_1vs1
import time

import json


from pongranker.models import Player, Game, Match, MatchGame
from django.contrib.auth.models import User

def home(request):
    player_list = Player.objects.order_by('-elo_singles_ranking','-total_singles_wins')
    template = loader.get_template('pongranker/index.html')
    context = RequestContext(request, {
        'player_list': player_list,
    })
    return HttpResponse(template.render(context))

def players(request):
    player_list = User.objects.order_by('first_name', 'last_name')

    template = loader.get_template('pongranker/players.html')
    context = RequestContext(request, {
        'player_list': player_list,
    })
    return HttpResponse(template.render(context))

def leaderboard(request):
    player_list = Player.objects.order_by('-elo_singles_ranking','-total_singles_wins')[:3]
    template = loader.get_template('pongranker/leaderboard.html')
    context = RequestContext(request, {
        'player_list': player_list,
    })
    return HttpResponse(template.render(context))

def player_detail(request, player_uname):

    context = RequestContext(request)
    try:
      player = User.objects.filter(username=player_uname)[0]
    except User.DoesNotExist:
      raise Http404

    # TODO: change this
    return render_to_response(
            'pongranker/404.html',
            {'player': player},
            context)


def add_game(request):
    context = RequestContext(request)

    if request.method == 'POST':
      # check that we have some necessary stuff

      error_msg = ""
      player_1_scores = []
      player_3_scores = []

      player_1_scores.append(int(request.POST['score_1_1']))
      player_3_scores.append(int(request.POST['score_2_1']))



      if 'player_1' not in request.POST or not request.POST['player_1']:
        error_msg = "Player 1 not given"
      elif 'player_3' not in request.POST or not request.POST['player_3']:
        error_msg = "Player 2 not given"


      for score in player_1_scores:
        if score < 0:
          error_msg = "Score may not be negative"
      for score in player_3_scores:
        if score < 0:
          error_msg = "Score may not be negative"


      if error_msg:
        return render_to_response(
              'pongranker/add_game.html',
              {'error_msg': error_msg},
              context)

      # we've reached here inputs are good.
      p1_email = request.POST['player_1']
      p3_email = request.POST['player_3']
      player_1 = Player.objects.get(user=User.objects.get(username=p1_email))
      player_3 = Player.objects.get(user=User.objects.get(username=p3_email))

      # order names alphabetically
      player_1_full_name  = (player_1.user.first_name + " " + player_1.user.last_name).lower()
      player_3_full_name  = (player_3.user.first_name + " " + player_3.user.last_name).lower()

      score_list = []

      if player_1_full_name <= player_3_full_name:
        player_1_name  = player_1.user.first_name + " " + player_1.user.last_name[0]
        player_3_name  = player_3.user.first_name + " " + player_3.user.last_name[0]
        i = 0
        for score in player_1_scores:
          score_list.append((score, player_3_scores[i]))
          i = i+1

      else:
        player_3_name  = player_1.user.first_name + " " + player_1.user.last_name[0]
        player_1_name  = player_3.user.first_name + " " + player_3.user.last_name[0]

        i = 0
        for score in player_3_scores:
          score_list.append((score, player_1_scores[i]))
          i = i+1

      match = Match(player_1=player_1_name, player_2=player_3_name)
      match.timestamp = time.time()
      game_list = []
      for score in score_list:
        game = MatchGame(score_1=score[0],
                       score_2=score[1])

        game.full_clean()
        game.save()
        game_list.append(game)

        old_ratings = (player_1.elo_singles_ranking, player_3.elo_singles_ranking)

        if game.score_1 > game.score_2:
          new_ratings = rate_1vs1(player_1.elo_singles_ranking, player_3.elo_singles_ranking)
          player_1.elo_singles_ranking = round(new_ratings[0])
          player_3.elo_singles_ranking = round(new_ratings[1])
          player_1.total_singles_wins += 1
          player_3.total_singles_losses += 1
          match.p1_wins += 1
          match.p1_point_change = player_1.elo_singles_ranking - old_ratings[0]
          match.p2_point_change = player_3.elo_singles_ranking - old_ratings[1]
        else:
          new_ratings = rate_1vs1(player_3.elo_singles_ranking, player_1.elo_singles_ranking)
          player_3.elo_singles_ranking = round(new_ratings[0])
          player_1.elo_singles_ranking = round(new_ratings[1])
          player_3.total_singles_wins += 1
          player_1.total_singles_losses += 1
          match.p2_wins += 1
          match.p1_point_change = player_1.elo_singles_ranking - old_ratings[1]
          match.p2_point_change = player_3.elo_singles_ranking - old_ratings[0]


      match.full_clean()
      match.save()

      for g in game_list:
        match.games.add(g)

      match.save()

      player_1.matches.add(match)
      player_3.matches.add(match)

      player_1.save()
      player_3.save()

      game_added = True

      return render_to_response(
            'pongranker/add_game.html',
            {'post_game_add': game_added},
            context)
    else:
      player_list = User.objects.order_by('first_name', 'last_name')

      return render_to_response(
            'pongranker/add_game.html',
            {'player_list': player_list},
            context)

def register(request):
    # Like before, get the request's context.
    context = RequestContext(request)

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.

        # If the two forms are valid...
        # Save the user's form data to the database.


        user = User(username=request.POST['email'], email=request.POST['email'], password=request.POST['password'],
                    first_name=request.POST['first_name'], last_name=request.POST['last_name'],)



        # Now we hash the password with the set_password method.
        # Once hashed, we can update the user object.
        user.set_password(user.password)
        try:
          user.save()
        except IntegrityError:
          integrity_error = True
          return render_to_response(
            'pongranker/register.html',
            {'integrity_error': integrity_error},
            context)

        player = Player(user=user)
        player.save()

        # Update our variable to tell the template registration was successful.
        registered = True
        auth_user = authenticate(username=user.username, password=user.password)

        if auth_user is not None:
          login(request,auth_user)

        return redirect('pongranker.views.player_detail', player_uname=user.username)


    # Render the template depending on the context.
    return render_to_response(
            'pongranker/register.html',
            {'registered': registered},
            context)

def sign_in(request):

    context = RequestContext(request)
    disabled_account = False
    if request.method == 'POST':
      username = request.POST['email']
      password = request.POST['password']
      user = authenticate(username=username, password=password)

      if user is not None:
        if user.is_active:
          login(request,user)
          return redirect('pongranker.views.player_detail', player_uname=user.username)
      else:
        disabled_account = True

    return render_to_response(
          'pongranker/login.html',
          {'disabled_account': disabled_account},
          context)

def sign_out(request):
    context = RequestContext(request)

    logout(request)

    return redirect('pongranker.views.home')

def unknown(request):
    raise Http404
# Create your views here.



