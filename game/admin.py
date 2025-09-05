from django.contrib import admin
from .models import Weapon, Monster, GameSession, Character, BattleLog

admin.site.register(Weapon)
admin.site.register(Monster)
admin.site.register(GameSession)
admin.site.register(Character)
admin.site.register(BattleLog)
