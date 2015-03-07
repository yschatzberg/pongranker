from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.db import IntegrityError
from django.template import RequestContext, loader
from django.contrib.auth import authenticate, login, logout



from pongranker.models import Player
from pongranker.api.views import post_match
from django.contrib.auth.models import User
import json

def home(request):
    template = loader.get_template('pongranker/index.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))

def doubles(request):
    template = loader.get_template('pongranker/doubles.html')
    context = RequestContext(request)
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

      return post_match(request)

      # if not response['error']:
       #  game_added = True

      # return render_to_response(
      #      'pongranker/add_game.html',
      #      {'post_game_add': game_added},
      #      context)
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



