import random

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .battle_engine import BattleEngine
from .models import Character, Weapon, Monster, GameSession, BattleLog
from .serializers import CharacterSerializer, WeaponSerializer, MonsterSerializer


def index(request):
    return render(request, 'index.html')


@api_view(['POST'])
def create_character(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # Удаляем старую сессию если есть
    GameSession.objects.filter(session_key=session_key).delete()

    # Создаем новую игровую сессию
    game_session = GameSession.objects.create(session_key=session_key)

    # Генерируем случайные характеристики
    strength = random.randint(1, 3)
    agility = random.randint(1, 3)
    endurance = random.randint(1, 3)

    character_class = request.data.get('class')

    # Получаем начальное оружие
    weapon_map = {'rogue': 'Кинжал', 'warrior': 'Меч', 'barbarian': 'Дубина'}

    initial_weapon = Weapon.objects.get(name=weapon_map[character_class])

    # Создаем персонажа с начальным уровнем в выбранном классе
    character = Character.objects.create(
        game_session=game_session,
        strength=strength,
        agility=agility,
        endurance=endurance,
        current_weapon=initial_weapon,
    )

    # Устанавливаем уровень в выбранном классе
    if character_class == 'rogue':
        character.rogue_level = 1
    elif character_class == 'warrior':
        character.warrior_level = 1
    elif character_class == 'barbarian':
        character.barbarian_level = 1

    character.save()

    serializer = CharacterSerializer(character)
    return Response(
        {
            'character': serializer.data,
            'stats': {'strength': strength, 'agility': agility, 'endurance': endurance},
        }
    )


@api_view(['GET'])
def get_character(request):
    session_key = request.session.session_key
    if not session_key:
        return Response({'error': 'No active session'}, status=400)

    try:
        game_session = GameSession.objects.get(session_key=session_key)
        character = Character.objects.get(game_session=game_session)
        serializer = CharacterSerializer(character)
        return Response(serializer.data)
    except (GameSession.DoesNotExist, Character.DoesNotExist):
        return Response({'error': 'Character not found'}, status=404)


@api_view(['POST'])
def start_battle(request):
    session_key = request.session.session_key
    if not session_key:
        return Response({'error': 'No active session'}, status=400)

    try:
        game_session = GameSession.objects.get(session_key=session_key)
        character = Character.objects.get(game_session=game_session)

        # Выбираем случайного монстра
        monsters = Monster.objects.all()
        monster = random.choice(monsters)

        # Создаем экземпляр боевого движка
        battle_engine = BattleEngine(character, monster)
        battle_result = battle_engine.fight()

        # Сохраняем лог боя
        BattleLog.objects.create(
            game_session=game_session,
            battle_number=character.monsters_defeated + 1,
            log_data=battle_result['log'],
            winner=battle_result['winner'],
        )

        if battle_result['winner'] == 'character':
            character.monsters_defeated += 1
            character.current_health = character.max_health  # Восстанавливаем здоровье
            character.save()

        return Response(
            {
                'battle_result': battle_result,
                'monster': MonsterSerializer(monster).data,
                'character': CharacterSerializer(character).data,
            }
        )

    except (GameSession.DoesNotExist, Character.DoesNotExist):
        return Response({'error': 'Character not found'}, status=404)


@api_view(['POST'])
def level_up_character(request):
    session_key = request.session.session_key
    character_class = request.data.get('class')

    try:
        game_session = GameSession.objects.get(session_key=session_key)
        character = Character.objects.get(game_session=game_session)

        success = character.level_up_class(character_class)

        if success:
            return Response(
                {
                    'character': CharacterSerializer(character).data,
                    'message': f'Уровень {character_class} повышен!',
                }
            )
        else:
            return Response({'error': 'Максимальный уровень достигнут'}, status=400)

    except (GameSession.DoesNotExist, Character.DoesNotExist):
        return Response({'error': 'Character not found'}, status=404)


@api_view(['POST'])
def change_weapon(request):
    session_key = request.session.session_key
    weapon_id = request.data.get('weapon_id')

    try:
        game_session = GameSession.objects.get(session_key=session_key)
        character = Character.objects.get(game_session=game_session)
        weapon = Weapon.objects.get(id=weapon_id)

        old_weapon = character.current_weapon
        character.current_weapon = weapon
        character.save()

        return Response(
            {
                'character': CharacterSerializer(character).data,
                'old_weapon': WeaponSerializer(old_weapon).data,
                'new_weapon': WeaponSerializer(weapon).data,
            }
        )

    except (GameSession.DoesNotExist, Character.DoesNotExist):
        return Response({'error': 'Character not found'}, status=404)
    except Weapon.DoesNotExist:
        return Response({'error': 'Weapon not found'}, status=404)
