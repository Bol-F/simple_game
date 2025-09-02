# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path(
        'api/character/creation/', views.CharacterCreationView.as_view(), name='character_creation'
    ),
    path('api/character/current/', views.CurrentCharacterView.as_view(), name='current_character'),
    path('api/battle/', views.BattleView.as_view(), name='battle'),
    path('api/level-up/', views.LevelUpView.as_view(), name='level_up'),
    path('api/weapon-selection/', views.WeaponSelectionView.as_view(), name='weapon_selection'),
    # Template views
    path('character-creation/', views.character_creation, name='character_creation_page'),
    path('battle/', views.battle, name='battle_page'),
    path('level-up/', views.level_up, name='level_up_page'),
    path('weapon-selection/', views.weapon_selection, name='weapon_selection_page'),
    path('game-over/', views.game_over, name='game_over_page'),
]
