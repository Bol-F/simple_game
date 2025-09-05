from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/character/create/', views.create_character, name='create_character'),
    path('api/character/status/', views.get_character, name='get_character'),
    path('api/battle/start/', views.start_battle, name='start_battle'),
    path('api/character/levelup/', views.level_up_character, name='level_up_character'),
    path('api/character/weapon/', views.change_weapon, name='change_weapon'),
]
