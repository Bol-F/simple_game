from rest_framework import serializers

from .models import Character, Weapon, Monster


class WeaponSerializer(serializers.ModelSerializer):
    weapon_type_display = serializers.CharField(source='get_weapon_type_display', read_only=True)

    class Meta:
        model = Weapon
        fields = ['id', 'name', 'damage', 'weapon_type', 'weapon_type_display']


class CharacterSerializer(serializers.ModelSerializer):
    current_weapon = WeaponSerializer(read_only=True)

    class Meta:
        model = Character
        fields = [
            'strength',
            'agility',
            'endurance',
            'rogue_level',
            'warrior_level',
            'barbarian_level',
            'current_health',
            'max_health',
            'current_weapon',
            'monsters_defeated',
            'total_level',
        ]


class MonsterSerializer(serializers.ModelSerializer):
    reward_weapon = WeaponSerializer(read_only=True)

    class Meta:
        model = Monster
        fields = [
            'name',
            'health',
            'weapon_damage',
            'strength',
            'agility',
            'endurance',
            'special_ability',
            'reward_weapon',
        ]
