# game/admin.py
from django.contrib import admin

from .models import CharacterClass, Weapon, Monster, GameSession

admin.site.register(CharacterClass)
admin.site.register(Weapon)
admin.site.register(Monster)
admin.site.register(GameSession)
