from django.urls import path

from . import views

urlpatterns = [
    path(
        "api/character/creation/",
        views.CharacterCreationView.as_view(),
        name="character_creation_api",
    ),
    path("api/battle/", views.BattleView.as_view(), name="battle_api"),
    path("api/level-up/", views.LevelUpView.as_view(), name="level_up_api"),
    path(
        "api/weapon-selection/",
        views.WeaponSelectionView.as_view(),
        name="weapon_selection_api",
    ),
    path("character-creation/", views.character_creation, name="character_creation"),
    path("battle/", views.battle, name="battle"),
    path("level-up/", views.level_up, name="level_up"),
    path("weapon-selection/", views.weapon_selection, name="weapon_selection"),
    path("game-over/", views.game_over, name="game_over"),
]
