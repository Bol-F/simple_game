from django.db import models


class CharacterClass(models.TextChoices):
    ROGUE = 'rogue', 'Разбойник'
    WARRIOR = 'warrior', 'Воин'
    BARBARIAN = 'barbarian', 'Варвар'


class WeaponType(models.TextChoices):
    SLASHING = 'slashing', 'Рубящий'
    CRUSHING = 'crushing', 'Дробящий'
    PIERCING = 'piercing', 'Колющий'


class Weapon(models.Model):
    name = models.CharField(max_length=100)
    damage = models.IntegerField()
    weapon_type = models.CharField(max_length=20, choices=WeaponType.choices)

    def __str__(self):
        return f"{self.name} ({self.damage} урон, {self.get_weapon_type_display()})"


class Monster(models.Model):
    name = models.CharField(max_length=100)
    health = models.IntegerField()
    weapon_damage = models.IntegerField()
    strength = models.IntegerField()
    agility = models.IntegerField()
    endurance = models.IntegerField()
    special_ability = models.TextField(blank=True)
    reward_weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GameSession(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Character(models.Model):
    game_session = models.OneToOneField(GameSession, on_delete=models.CASCADE)

    # Базовые характеристики
    strength = models.IntegerField()
    agility = models.IntegerField()
    endurance = models.IntegerField()

    # Уровни классов
    rogue_level = models.IntegerField(default=0)
    warrior_level = models.IntegerField(default=0)
    barbarian_level = models.IntegerField(default=0)

    # Текущее состояние
    current_health = models.IntegerField()
    max_health = models.IntegerField()
    current_weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE)

    # Прогресс
    monsters_defeated = models.IntegerField(default=0)
    total_level = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Расчет максимального здоровья при создании
            self.max_health = self.calculate_max_health()
            self.current_health = self.max_health
        super().save(*args, **kwargs)

    def calculate_max_health(self):
        total_hp = 0
        total_hp += self.rogue_level * 4
        total_hp += self.warrior_level * 5
        total_hp += self.barbarian_level * 6
        total_hp += self.endurance * self.total_level
        return max(total_hp, 1)

    def get_total_damage(self):
        return self.current_weapon.damage + self.strength

    def level_up_class(self, character_class):
        if self.total_level >= 3:
            return False

        if character_class == 'rogue':
            self.rogue_level += 1
        elif character_class == 'warrior':
            self.warrior_level += 1
        elif character_class == 'barbarian':
            self.barbarian_level += 1

        self.total_level += 1
        old_max_health = self.max_health
        self.max_health = self.calculate_max_health()
        self.current_health = self.max_health

        # Применяем бонусы уровней
        if character_class == 'rogue' and self.rogue_level == 2:
            self.agility += 1
        elif character_class == 'warrior' and self.warrior_level == 3:
            self.strength += 1
        elif character_class == 'barbarian' and self.barbarian_level == 3:
            self.endurance += 1

        self.save()
        return True


class BattleLog(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE)
    battle_number = models.IntegerField()
    log_data = models.TextField()  # JSON строка с логом боя
    winner = models.CharField(max_length=20)  # 'character' или 'monster'
    created_at = models.DateTimeField(auto_now_add=True)
