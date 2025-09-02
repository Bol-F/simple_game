import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from game.models import CharacterClass, Weapon, Monster

# Clear existing data
Weapon.objects.all().delete()
CharacterClass.objects.all().delete()
Monster.objects.all().delete()

# Create weapons
weapons = {
    "sword": Weapon.objects.create(name="Меч", damage=3, damage_type="slashing"),
    "club": Weapon.objects.create(name="Дубина", damage=3, damage_type="bludgeoning"),
    "dagger": Weapon.objects.create(name="Кинжал", damage=2, damage_type="piercing"),
    "axe": Weapon.objects.create(name="Топор", damage=4, damage_type="slashing"),
    "spear": Weapon.objects.create(name="Копье", damage=3, damage_type="piercing"),
    "legendary_sword": Weapon.objects.create(
        name="Легендарный Меч", damage=10, damage_type="slashing"
    ),
}

# Create character classes
CharacterClass.objects.create(
    name="Воин",
    health_per_level=5,
    initial_weapon=weapons["sword"],
    level1_bonus="Порыв к действию: В первый ход наносит двойной урон оружием",
    level2_bonus="Щит: -3 к получаемому урону если сила персонажа выше силы атакующего",
    level3_bonus="Сила +1",
)

CharacterClass.objects.create(
    name="Варвар",
    health_per_level=6,
    initial_weapon=weapons["club"],
    level1_bonus="Ярость: +2 к урону в первые 3 хода, потом -1 к урону",
    level2_bonus="Каменная кожа: Получаемый урон снижается на значение выносливости",
    level3_bonus="Выносливость +1",
)

CharacterClass.objects.create(
    name="Разбойник",
    health_per_level=4,
    initial_weapon=weapons["dagger"],
    level1_bonus="Скрытая атака: +1 к урону если ловкость персонажа выше ловкости цели",
    level2_bonus="Ловкость +1",
    level3_bonus="Яд: Наносит дополнительные +1 урона на втором ходу, +2 на третьем и так далее",
)

print("Database populated successfully!")
