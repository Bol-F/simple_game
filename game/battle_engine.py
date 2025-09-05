import json
import random


class BattleEngine:
    def __init__(self, character, monster):
        self.character = character
        self.monster = monster
        self.character_hp = character.current_health
        self.monster_hp = monster.health
        self.turn_counter = 0
        self.battle_log = []

    def fight(self):
        # Определяем кто ходит первым
        if self.character.agility > self.monster.agility:
            first_attacker = 'character'
        elif self.character.agility < self.monster.agility:
            first_attacker = 'monster'
        else:
            first_attacker = 'character'  # При равной ловкости персонаж ходит первым

        self.log(
            f"Бой начинается! {self.character_hp} HP vs {self.monster.name} {self.monster_hp} HP"
        )

        current_attacker = first_attacker

        while self.character_hp > 0 and self.monster_hp > 0:
            self.turn_counter += 1

            if current_attacker == 'character':
                self.character_attack()
                current_attacker = 'monster'
            else:
                self.monster_attack()
                current_attacker = 'character'

        # Определяем победителя
        if self.character_hp > 0:
            winner = 'character'
            self.log("🎉 Персонаж победил!")
        else:
            winner = 'monster'
            self.log("💀 Персонаж погиб...")

        return {
            'winner': winner,
            'character_hp': max(0, self.character_hp),
            'monster_hp': max(0, self.monster_hp),
            'log': json.dumps(self.battle_log, ensure_ascii=False),
        }

    def character_attack(self):
        self.log(f"Ход {self.turn_counter}: Персонаж атакует!")

        # Проверяем попадание
        if not self.check_hit(self.character.agility, self.monster.agility):
            self.log("❌ Промах!")
            return

        # Базовый урон
        base_damage = self.character.current_weapon.damage + self.character.strength

        # Применяем способности персонажа
        damage = self.apply_character_abilities(base_damage)

        # Применяем защитные способности монстра
        final_damage = self.apply_monster_defense(damage)

        if final_damage > 0:
            self.monster_hp -= final_damage
            self.log(
                f"💥 Нанесено {final_damage} урона! У {self.monster.name} осталось {max(0, self.monster_hp)} HP"
            )
        else:
            self.log("🛡️ Урон полностью поглощен!")

    def monster_attack(self):
        self.log(f"Ход {self.turn_counter}: {self.monster.name} атакует!")

        # Проверяем попадание
        if not self.check_hit(self.monster.agility, self.character.agility):
            self.log("❌ Промах!")
            return

        # Базовый урон монстра
        base_damage = self.monster.weapon_damage + self.monster.strength

        # Применяем способности монстра
        damage = self.apply_monster_abilities(base_damage)

        # Применяем защитные способности персонажа
        final_damage = self.apply_character_defense(damage)

        if final_damage > 0:
            self.character_hp -= final_damage
            self.log(f"💥 Получено {final_damage} урона! Осталось {max(0, self.character_hp)} HP")
        else:
            self.log("🛡️ Урон полностью поглощен!")

    def check_hit(self, attacker_agility, target_agility):
        total_agility = attacker_agility + target_agility
        roll = random.randint(1, total_agility)
        return roll > target_agility

    def apply_character_abilities(self, base_damage):
        damage = base_damage

        # Способности разбойника
        if self.character.rogue_level >= 1:
            # Скрытая атака
            if self.character.agility > self.monster.agility:
                damage += 1
                self.log("🗡️ Скрытая атака! +1 урон")

            # Яд (с 3 уровня)
            if self.character.rogue_level >= 3:
                poison_damage = self.turn_counter - 1  # Яд накапливается с каждым ходом
                if poison_damage > 0:
                    damage += poison_damage
                    self.log(f"☠️ Яд! +{poison_damage} урон")

        # Способности воина
        if self.character.warrior_level >= 1:
            # Порыв к действию (первый ход)
            if self.turn_counter == 1:
                weapon_damage = self.character.current_weapon.damage
                damage += weapon_damage
                self.log(f"⚡ Порыв к действию! +{weapon_damage} урон")

        # Способности варвара
        if self.character.barbarian_level >= 1:
            # Ярость (первые 3 хода +2, потом -1)
            if self.turn_counter <= 3:
                damage += 2
                self.log("🔥 Ярость! +2 урон")
            else:
                damage -= 1
                self.log("😤 Усталость от ярости! -1 урон")

        return max(0, damage)

    def apply_character_defense(self, incoming_damage):
        damage = incoming_damage

        # Способности воина
        if self.character.warrior_level >= 2:
            # Щит
            if self.character.strength > self.monster.strength:
                damage -= 3
                self.log("🛡️ Щит! -3 урон")

        # Способности варвара
        if self.character.barbarian_level >= 2:
            # Каменная кожа
            damage -= self.character.endurance
            self.log(f"🗿 Каменная кожа! -{self.character.endurance} урон")

        return max(0, damage)

    def apply_monster_abilities(self, base_damage):
        damage = base_damage

        # Особые способности монстров
        if self.monster.name == "Призрак":
            # Скрытая атака как у разбойника
            if self.monster.agility > self.character.agility:
                damage += 1
                self.log("👻 Призрак использует скрытую атаку! +1 урон")

        elif self.monster.name == "Дракон":
            # Дыхание огнем каждый 3-й ход
            if self.turn_counter % 3 == 0:
                damage += 3
                self.log("🔥 Дракон дышит огнем! +3 урон")

        return damage

    def apply_monster_defense(self, incoming_damage):
        damage = incoming_damage

        if self.monster.name == "Скелет":
            # Двойной урон от дробящего оружия
            if self.character.current_weapon.weapon_type == 'crushing':
                damage *= 2
                self.log("💀 Скелет уязвим к дробящему! Урон удвоен")

        elif self.monster.name == "Слайм":
            # Рубящее оружие не наносит урона (кроме бонусов)
            if self.character.current_weapon.weapon_type == 'slashing':
                weapon_damage = self.character.current_weapon.damage
                damage -= weapon_damage
                self.log("🟢 Слайм невосприимчив к рубящему оружию!")

        elif self.monster.name == "Голем":
            # Каменная кожа как у варвара
            damage -= self.monster.endurance
            self.log(f"🗿 Голем использует каменную кожу! -{self.monster.endurance} урон")

        return max(0, damage)

    def log(self, message):
        self.battle_log.append(message)
