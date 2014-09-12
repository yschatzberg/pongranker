from django.contrib import admin
from pongranker.models import Player, SinglesMatchup, SinglesMatchupScore, Game

class SinglesMatchupScoreInline(admin.StackedInline):
    model = SinglesMatchupScore
    extra = 2

class PlayerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Player Information', {'fields': ['user.first_name','user.last_name', 'user.email']}),
        ('Game Statistics', {'fields': ['total_singles_wins',
         'total_singles_losses', 'elo_singles_ranking']}),
    ]




admin.site.register(Player, PlayerAdmin)
admin.site.register(SinglesMatchup)
admin.site.register(SinglesMatchupScore)
admin.site.register(Game)




# Register your models here.
