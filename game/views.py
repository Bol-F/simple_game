# game/views.py
import logging
import random

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CharacterClass, Weapon, Monster, GameSession
from .serializers import CharacterClassSerializer, WeaponSerializer, MonsterSerializer
from .utils import simulate_battle, level_up_character, change_weapon
from .validators import validate_character_attributes, validate_class_id

logger = logging.getLogger(__name__)


def get_game_session(session_key):
    """Safely retrieve game session with proper error handling"""
    if not session_key:
        logger.warning("Attempt to access game session without valid session key")
        return None, Response(
            {'error': 'Session not found. Please create a character first.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        return GameSession.objects.get(session_key=session_key), None
    except GameSession.DoesNotExist:
        logger.warning(f"Game session not found for key: {session_key}")
        return None, Response(
            {'error': 'Character not found. Please create a character first.'},
            status=status.HTTP_404_NOT_FOUND,
        )


# game/views.py
import logging
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import CharacterClass, Weapon, Monster, GameSession
from .serializers import CharacterClassSerializer, WeaponSerializer, MonsterSerializer
from .utils import simulate_battle, level_up_character, change_weapon

logger = logging.getLogger(__name__)


def get_game_session(session_key):
    """Safely retrieve game session with proper error handling"""
    if not session_key:
        logger.warning("Attempt to access game session without valid session key")
        return None, JsonResponse(
            {'error': 'Session not found. Please create a character first.'},
            status=status.HTTP_404_NOT_FOUND
        )

    try:
        return GameSession.objects.get(session_key=session_key), None
    except GameSession.DoesNotExist:
        logger.warning(f"Game session not found for key: {session_key}")
        return None, JsonResponse(
            {'error': 'Character not found. Please create a character first.'},
            status=status.HTTP_404_NOT_FOUND
        )


class CharacterCreationView(APIView):
    def get(self, request):
        try:
            classes = CharacterClass.objects.all()
            logger.info(f"Found {classes.count()} character classes")
            serializer = CharacterClassSerializer(classes, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving character classes: {str(e)}")
            return Response(
                {'error': 'Unable to retrieve character classes'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @method_decorator(csrf_exempt)
    def post(self, request):
        logger.info(f"Received character creation request from session: {request.session.session_key}")

        # Parse JSON data if content-type is application/json
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Invalid JSON data'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            data = request.POST

        # Validate required parameters
        required_fields = ['class_id', 'strength', 'agility', 'endurance']
        if not all(field in data for field in required_fields):
            logger.warning("Missing required fields in character creation")
            return Response(
                {'error': 'Missing required fields: class_id, strength, agility, endurance'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            class_id = data.get('class_id')
            strength = int(data.get('strength'))
            agility = int(data.get('agility'))
            endurance = int(data.get('endurance'))

            # Validate attributes
            min_value, max_value = 1, 20
            if any(attr < min_value or attr > max_value for attr in [strength, agility, endurance]):
                return Response(
                    {'error': f'Attributes must be between {min_value} and {max_value}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate class exists
            try:
                character_class = CharacterClass.objects.get(id=class_id)
            except CharacterClass.DoesNotExist:
                return Response(
                    {'error': 'Class not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Ensure session exists
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key

            # Create character data structure
            character_data = {
                'class_levels': {character_class.name.lower(): 1},
                'attributes': {
                    'strength': strength,
                    'agility': agility,
                    'endurance': endurance
                },
                'weapon': {
                    'id': character_class.initial_weapon.id,
                    'name': character_class.initial_weapon.name,
                    'damage': character_class.initial_weapon.damage,
                    'damage_type': character_class.initial_weapon.damage_type
                },
                'health': character_class.health_per_level + endurance,
                'max_health': character_class.health_per_level + endurance,
                'total_level': 1,
                'battle_log': [],
                'consecutive_wins': 0
            }

            logger.info(f"Creating character for session {session_key}")

            # Save or update game session
            game_session, created = GameSession.objects.update_or_create(
                session_key=session_key,
                defaults={
                    'character_data': character_data,
                    'consecutive_wins': 0
                }
            )

            logger.info(f"Game session {'created' if created else 'updated'}")
            return Response(character_data)

        except ValueError:
            logger.error("Invalid integer value provided for attributes")
            return Response(
                {'error': 'Strength, agility, and endurance must be valid integers'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating character: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CurrentCharacterView(APIView):
    def get(self, request):
        session_key = request.session.session_key
        game_session, error_response = get_game_session(session_key)
        if error_response:
            return error_response

        logger.info(f"Retrieved character for session: {session_key}")
        return Response(game_session.character_data)


class BattleView(APIView):
    def get(self, request):
        try:
            # Get random monster
            monsters = list(Monster.objects.all())
            if not monsters:
                return Response(
                    {'error': 'No monsters available'}, status=status.HTTP_404_NOT_FOUND
                )

            monster = random.choice(monsters)
            serializer = MonsterSerializer(monster)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving monster: {str(e)}")
            return Response(
                {'error': 'Unable to retrieve monsters'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @method_decorator(csrf_protect)
    def post(self, request):
        session_key = request.session.session_key
        game_session, error_response = get_game_session(session_key)
        if error_response:
            return error_response

        # Validate monster_id
        monster_id = request.data.get('monster_id')
        if not monster_id:
            return Response({'error': 'monster_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            monster = Monster.objects.get(id=monster_id)
        except Monster.DoesNotExist:
            return Response({'error': 'Monster not found'}, status=status.HTTP_404_NOT_FOUND)

        # Simulate battle
        character_data = game_session.character_data
        battle_result = simulate_battle(character_data, monster)

        if battle_result['result'] == 'win':
            game_session.consecutive_wins += 1
            # Heal character but don't exceed max health
            character_data['health'] = min(
                character_data['max_health'],
                character_data['health'] + character_data['endurance'] // 2,
            )
            character_data['consecutive_wins'] = game_session.consecutive_wins
            game_session.character_data = character_data
            game_session.save()

            # Check if game is won (5 consecutive wins)
            battle_result['game_won'] = game_session.consecutive_wins >= 5

            if battle_result['game_won']:
                logger.info(f"Player won the game in session {session_key}")

            battle_result['reward_weapon'] = WeaponSerializer(monster.reward_weapon).data
        else:
            # Defeat - reset session
            game_session.delete()
            logger.info(f"Player defeated in session {session_key}")

        return Response(battle_result)


class LevelUpView(APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        session_key = request.session.session_key
        game_session, error_response = get_game_session(session_key)
        if error_response:
            return error_response

        class_name = request.data.get('class_name')
        if not class_name:
            return Response({'error': 'class_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            character_data = level_up_character(game_session.character_data, class_name)
            game_session.character_data = character_data
            game_session.save()
            return Response(character_data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error during level up: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WeaponSelectionView(APIView):
    @method_decorator(csrf_protect)
    def post(self, request):
        session_key = request.session.session_key
        game_session, error_response = get_game_session(session_key)
        if error_response:
            return error_response

        weapon_id = request.data.get('weapon_id')
        if not weapon_id:
            return Response({'error': 'weapon_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            weapon = Weapon.objects.get(id=weapon_id)
        except Weapon.DoesNotExist:
            return Response({'error': 'Weapon not found'}, status=status.HTTP_404_NOT_FOUND)

        character_data = change_weapon(game_session.character_data, weapon)
        game_session.character_data = character_data
        game_session.save()

        return Response(character_data)


# Template views
def character_creation(request):
    try:
        classes = CharacterClass.objects.all()
        return render(request, 'character_creation.html', {'classes': classes})
    except Exception as e:
        logger.error(f"Error loading character creation: {str(e)}")
        # Fallback to a simple error message
        return HttpResponse("Error loading character creation. Please try again later.", status=500)


def battle(request):
    return render(request, 'battle.html')


def level_up(request):
    try:
        classes = CharacterClass.objects.all()
        return render(request, 'level_up.html', {'classes': classes})
    except Exception as e:
        logger.error(f"Error loading level up: {str(e)}")
        # Fallback to a simple error message
        return HttpResponse("Error loading level up page. Please try again later.", status=500)


def weapon_selection(request):
    return render(request, 'weapon_selection.html')


def game_over(request):
    return render(request, 'game_over.html')
