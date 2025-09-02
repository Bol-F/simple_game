import random

from django.db import models


def rand_1_to_3():
    return random.randint(1, 3)


class CharacterClass(models.Model):
    name = models.CharField(max_length=20)
    health_per_level = models.IntegerField()
    initial_weapon = models.ForeignKey('Weapon', on_delete=models.CASCADE)
    level1_bonus = models.TextField()
    level2_bonus = models.TextField()
    level3_bonus = models.TextField()

    def __str__(self):
        return self.name


class Weapon(models.Model):
    DAMAGE_TYPES = (
        ('slashing', 'Рубящий'),
        ('bludgeoning', 'Дробящий'),
        ('piercing', 'Колющий'),
    )

    name = models.CharField(max_length=30)
    damage = models.IntegerField()
    damage_type = models.CharField(max_length=15, choices=DAMAGE_TYPES)

    def __str__(self):
        return self.name


class Monster(models.Model):
    name = models.CharField(max_length=30)
    health = models.IntegerField()
    weapon_damage = models.IntegerField()
    strength = models.IntegerField()
    agility = models.IntegerField()
    endurance = models.IntegerField()
    features = models.TextField(blank=True)
    reward_weapon = models.ForeignKey('Weapon', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GameSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    character_data = models.JSONField(default=dict)
    consecutive_wins = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"GameSession {self.session_key}"
