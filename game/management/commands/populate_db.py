from django.core.management.base import BaseCommand

from game.models import CharacterClass, Weapon, Monster


class Command(BaseCommand):
    help = 'Populates the database with initial game data'

    def handle(self, *args, **options):
        # Clear existing data
        Weapon.objects.all().delete()
        CharacterClass.objects.all().delete()
        Monster.objects.all().delete()

        # Create weapons
        weapons = {
            'sword': Weapon.objects.create(name='Меч', damage=3, damage_type='slashing'),
            'club': Weapon.objects.create(name='Дубина', damage=3, damage_type='bludgeoning'),
            'dagger': Weapon.objects.create(name='Кинжал', damage=2, damage_type='piercing'),
            'axe': Weapon.objects.create(name='Топор', damage=4, damage_type='slashing'),
            'spear': Weapon.objects.create(name='Копье', damage=3, damage_type='piercing'),
            'legendary_sword': Weapon.objects.create(name='Легендарный Меч', damage=10, damage_type='slashing'),
        }

        # Create character classes
        CharacterClass.objects.create(
            name='Воин',
            health_per_level=5,
            initial_weapon=weapons['sword'],
            level1_bonus='Порыв к действию: В первый ход наносит двойной урон оружием',
            level2_bonus='Щит: -3 к получаемому урону если сила персонажа выше силы атакующего',
            level3_bonus='Сила +1'
        )

        CharacterClass.objects.create(
            name='Варвар',
            health_per_level=6,
            initial_weapon=weapons['club'],
            level1_bonus='Ярость: +2 к урону в первые 3 хода, потом -1 к урону',
            level2_bonus='Каменная кожа: Получаемый урон снижается на значение выносливости',
            level3_bonus='Выносливость +1'
        )

        CharacterClass.objects.create(
            name='Разбойник',
            health_per_level=4,
            initial_weapon=weapons['dagger'],
            level1_bonus='Скрытая атака: +1 к урону если ловкость персонажа выше ловкости цели',
            level2_bonus='Ловкость +1',
            level3_bonus='Яд: Наносит дополнительные +1 урона на втором ходу, +2 на третьем и так далее'
        )

        # Create monsters
        Monster.objects.create(
            name='Гоблин',
            health=5,
            weapon_damage=2,
            strength=1,
            agility=1,
            endurance=1,
            features='',
            reward_weapon=weapons['dagger']
        )

        Monster.objects.create(
            name='Скелет',
            health=10,
            weapon_damage=2,
            strength=2,
            agility=2,
            endurance=1,
            features='Получает вдвое больше урона, если его бьют дробящим оружием',
            reward_weapon=weapons['club']
        )

        Monster.objects.create(
            name='Слайм',
            health=8,
            weapon_damage=1,
            strength=3,
            agility=1,
            endurance=2,
            features='Рубящее оружие не наносит ему урона (но урон от силы и прочих особенностей, даже "порыва к действию" воина, работает)',
            reward_weapon=weapons['spear']
        )

        Monster.objects.create(
            name='Призрак',
            health=6,
            weapon_damage=3,
            strength=1,
            agility=3,
            endurance=1,
            features='Есть способность "скрытая атака", как у разбойника 1-го уровня',
            reward_weapon=weapons['sword']
        )

        Monster.objects.create(
            name='Голем',
            health=10,
            weapon_damage=1,
            strength=3,
            agility=1,
            endurance=3,
            features='Есть способность "каменная кожа", как у Варвара 2-го уровня',
            reward_weapon=weapons['axe']
        )

        Monster.objects.create(
            name='Дракон',
            health=20,
            weapon_damage=4,
            strength=3,
            agility=3,
            endurance=3,
            features='Каждый 3-й ход дышит огнём, нанося дополнительно 3 урона',
            reward_weapon=weapons['legendary_sword']
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with initial game data')
        )
