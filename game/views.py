# game/views.py
import logging
import random

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CharacterClass, Weapon, Monster, GameSession
from .serializers import CharacterClassSerializer, WeaponSerializer, MonsterSerializer
from .utils import simulate_battle, level_up_character, change_weapon

logger = logging.getLogger(__name__)


class CharacterCreationView(APIView):
    def get(self, request):
        classes = CharacterClass.objects.all()
        serializer = CharacterClassSerializer(classes, many=True)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request):
        logger.info(f"Received character creation request: {request.data}")

        class_id = request.data.get('class_id')
        strength = request.data.get('strength', random.randint(1, 3))
        agility = request.data.get('agility', random.randint(1, 3))
        endurance = request.data.get('endurance', random.randint(1, 3))

        logger.info(f"Class ID: {class_id}, Strength: {strength}, Agility: {agility}, Endurance: {endurance}")

        # Ensure session exists
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key

        try:
            character_class = CharacterClass.objects.get(id=class_id)
            initial_weapon = character_class.initial_weapon

            character_data = {
                'class_levels': {character_class.name.lower(): 1},
                'attributes': {
                    'strength': strength,
                    'agility': agility,
                    'endurance': endurance
                },
                'weapon': {
                    'id': initial_weapon.id,
                    'name': initial_weapon.name,
                    'damage': initial_weapon.damage,
                    'damage_type': initial_weapon.damage_type
                },
                'health': character_class.health_per_level + endurance,
                'max_health': character_class.health_per_level + endurance,
                'total_level': 1,
                'battle_log': []
            }

            # Save or update game session
            game_session, created = GameSession.objects.get_or_create(
                session_key=session_key,
                defaults={'character_data': character_data, 'consecutive_wins': 0}
            )

            if not created:
                game_session.character_data = character_data
                game_session.consecutive_wins = 0
                game_session.save()

            logger.info(f"Character created successfully for session {session_key}")
            return Response(character_data)

        except CharacterClass.DoesNotExist:
            logger.error(f"Class with ID {class_id} not found")
            return Response({'error': 'Class not found'}, status=400)
        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            return Response({'error': 'Internal server error'}, status=500)


class BattleView(APIView):
    def get(self, request):
        # Get random monster
        monsters = list(Monster.objects.all())
        monster = random.choice(monsters)
        serializer = MonsterSerializer(monster)
        return Response(serializer.data)

    @csrf_exempt
    def post(self, request):
        session_key = request.session.session_key
        try:
            game_session = GameSession.objects.get(session_key=session_key)
        except GameSession.DoesNotExist:
            return Response({'error': 'No character found'}, status=400)

        character_data = game_session.character_data
        monster_id = request.data.get('monster_id')

        try:
            monster = Monster.objects.get(id=monster_id)
        except Monster.DoesNotExist:
            return Response({'error': 'Monster not found'}, status=400)

        # Simulate battle
        battle_result = simulate_battle(character_data, monster)

        if battle_result['result'] == 'win':
            game_session.consecutive_wins += 1
            character_data['health'] = character_data['max_health']  # Heal character
            game_session.character_data = character_data
            game_session.save()

            # Check if game is won (5 consecutive wins)
            if game_session.consecutive_wins >= 5:
                battle_result['game_won'] = True
            else:
                battle_result['game_won'] = False

            battle_result['reward_weapon'] = WeaponSerializer(monster.reward_weapon).data
        else:
            game_session.delete()  # Remove session on defeat

        return Response(battle_result)


class LevelUpView(APIView):
    @csrf_exempt
    def post(self, request):
        session_key = request.session.session_key
        try:
            game_session = GameSession.objects.get(session_key=session_key)
        except GameSession.DoesNotExist:
            return Response({'error': 'No character found'}, status=400)

        class_name = request.data.get('class_name')
        character_data = level_up_character(game_session.character_data, class_name)

        game_session.character_data = character_data
        game_session.save()

        return Response(character_data)


class WeaponSelectionView(APIView):
    @csrf_exempt
    def post(self, request):
        session_key = request.session.session_key
        try:
            game_session = GameSession.objects.get(session_key=session_key)
        except GameSession.DoesNotExist:
            return Response({'error': 'No character found'}, status=400)

        weapon_id = request.data.get('weapon_id')

        try:
            weapon = Weapon.objects.get(id=weapon_id)
        except Weapon.DoesNotExist:
            return Response({'error': 'Weapon not found'}, status=400)

        character_data = change_weapon(game_session.character_data, weapon)

        game_session.character_data = character_data
        game_session.save()

        return Response(character_data)


def character_creation(request):
    classes = CharacterClass.objects.all()
    return render(request, 'character_creation.html', {'classes': classes})


def battle(request):
    return render(request, 'battle.html')


def level_up(request):
    classes = CharacterClass.objects.all()
    return render(request, 'level_up.html', {'classes': classes})


def weapon_selection(request):
    return render(request, 'weapon_selection.html')


def game_over(request):
    return render(request, 'game_over.html')
