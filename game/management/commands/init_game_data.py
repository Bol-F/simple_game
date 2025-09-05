from django.core.management.base import BaseCommand

from game.models import Weapon, Monster


class Command(BaseCommand):
    help = 'Initialize game data: weapons and monsters'

    def handle(self, *args, **options):
        self.stdout.write('Создание оружия...')

        # Создаем оружие
        weapons_data = [
            {'name': 'Меч', 'damage': 3, 'weapon_type': 'slashing'},
            {'name': 'Дубина', 'damage': 3, 'weapon_type': 'crushing'},
            {'name': 'Кинжал', 'damage': 2, 'weapon_type': 'piercing'},
            {'name': 'Топор', 'damage': 4, 'weapon_type': 'slashing'},
            {'name': 'Копье', 'damage': 3, 'weapon_type': 'piercing'},
            {'name': 'Легендарный Меч', 'damage': 10, 'weapon_type': 'slashing'},
        ]

        for weapon_data in weapons_data:
            weapon, created = Weapon.objects.get_or_create(
                name=weapon_data['name'], defaults=weapon_data
            )
            if created:
                self.stdout.write(f'  ✓ Создано: {weapon.name}')
            else:
                self.stdout.write(f'  - Уже есть: {weapon.name}')

        self.stdout.write('Создание монстров...')

        # Получаем оружие для наград
        kinzhal = Weapon.objects.get(name='Кинжал')
        dubina = Weapon.objects.get(name='Дубина')
        kopie = Weapon.objects.get(name='Копье')
        mech = Weapon.objects.get(name='Меч')
        topor = Weapon.objects.get(name='Топор')
        legendary_sword = Weapon.objects.get(name='Легендарный Меч')

        # Создаем монстров
        monsters_data = [
            {
                'name': 'Гоблин',
                'health': 5,
                'weapon_damage': 2,
                'strength': 1,
                'agility': 1,
                'endurance': 1,
                'special_ability': '',
                'reward_weapon': kinzhal,
            },
            {
                'name': 'Скелет',
                'health': 10,
                'weapon_damage': 2,
                'strength': 2,
                'agility': 2,
                'endurance': 1,
                'special_ability': 'Получает вдвое больше урона от дробящего оружия',
                'reward_weapon': dubina,
            },
            {
                'name': 'Слайм',
                'health': 8,
                'weapon_damage': 1,
                'strength': 3,
                'agility': 1,
                'endurance': 2,
                'special_ability': 'Рубящее оружие не наносит ему урона',
                'reward_weapon': kopie,
            },
            {
                'name': 'Призрак',
                'health': 6,
                'weapon_damage': 3,
                'strength': 1,
                'agility': 3,
                'endurance': 1,
                'special_ability': 'Имеет способность "скрытая атака"',
                'reward_weapon': mech,
            },
            {
                'name': 'Голем',
                'health': 10,
                'weapon_damage': 1,
                'strength': 3,
                'agility': 1,
                'endurance': 3,
                'special_ability': 'Имеет способность "каменная кожа"',
                'reward_weapon': topor,
            },
            {
                'name': 'Дракон',
                'health': 20,
                'weapon_damage': 4,
                'strength': 3,
                'agility': 3,
                'endurance': 3,
                'special_ability': 'Каждый 3-й ход дышит огнём (+3 урона)',
                'reward_weapon': legendary_sword,
            },
        ]

        for monster_data in monsters_data:
            monster, created = Monster.objects.get_or_create(
                name=monster_data['name'], defaults=monster_data
            )
            if created:
                self.stdout.write(f'  ✓ Создан: {monster.name}')
            else:
                self.stdout.write(f'  - Уже есть: {monster.name}')

        self.stdout.write(self.style.SUCCESS('Инициализация данных завершена!'))
