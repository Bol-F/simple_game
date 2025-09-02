import random


# game/utils.py (add this function)
def create_character(character_class, strength, agility, endurance):
    """
    Create a new character with the given class and attributes
    """
    max_health = character_class.health_per_level + endurance

    character_data = {
        "class_levels": {character_class.name.lower(): 1},
        "attributes": {
            "strength": strength,
            "agility": agility,
            "endurance": endurance,
        },
        "weapon": {
            "id": character_class.initial_weapon.id,
            "name": character_class.initial_weapon.name,
            "damage": character_class.initial_weapon.damage,
            "damage_type": character_class.initial_weapon.damage_type,
        },
        "health": max_health,
        "max_health": max_health,
        "total_level": 1,
        "battle_log": [],
    }

    return character_data


def calculate_max_health(character_data):
    # Calculate max health based on class levels and endurance
    from .models import CharacterClass

    total_health = 0
    endurance = character_data["attributes"]["endurance"]

    for class_name, level in character_data["class_levels"].items():
        try:
            char_class = CharacterClass.objects.get(name__iexact=class_name)
            total_health += char_class.health_per_level * level
        except CharacterClass.DoesNotExist:
            continue

    return total_health + endurance


def simulate_battle(character_data, monster):
    battle_log = []
    char_health = character_data["health"]
    monster_health = monster.health

    # Determine who goes first
    char_agility = character_data["attributes"]["agility"]
    if char_agility >= monster.agility:
        attacker = "character"
    else:
        attacker = "monster"

    turn = 1
    character_turns = {}  # To track special abilities

    while char_health > 0 and monster_health > 0:
        if attacker == "character":
            # Character's turn to attack
            damage, log_entry = calculate_damage(
                character_data, monster, turn, character_turns
            )
            battle_log.append(log_entry)

            if damage > 0:
                monster_health -= damage
                battle_log.append(f"Персонаж наносит {damage} урона монстру.")
            else:
                battle_log.append("Персонаж промахивается!")

            # Check if monster is defeated
            if monster_health <= 0:
                battle_log.append("Монстр побежден!")
                result = "win"
                break

            attacker = "monster"

        else:
            # Monster's turn to attack
            hit_chance = random.randint(1, char_agility + monster.agility)
            if hit_chance <= char_agility:
                # Character dodges
                battle_log.append("Монстр атакует, но персонаж уворачивается!")
                damage = 0
            else:
                # Monster hits
                damage = monster.weapon_damage + monster.strength

                # Apply character defenses
                damage = apply_defenses(
                    character_data, monster, damage, turn, character_turns
                )

                if damage > 0:
                    char_health -= damage
                    battle_log.append(f"Монстр наносит {damage} урона персонажу.")
                else:
                    battle_log.append("Монстр атакует, но не наносит урона!")

            # Check if character is defeated
            if char_health <= 0:
                battle_log.append("Персонаж побежден!")
                result = "lose"
                break

            attacker = "character"
            turn += 1

    return {
        "result": result,
        "battle_log": battle_log,
        "character_health": max(0, char_health),
        "monster_health": max(0, monster_health),
    }


def calculate_damage(character_data, monster, turn, character_turns):
    # Check if attack hits
    char_agility = character_data["attributes"]["agility"]
    hit_chance = random.randint(1, char_agility + monster.agility)
    if hit_chance <= monster.agility:
        return 0, "Персонаж атакует, но монстр уворачивается!"

    # Base damage
    base_damage = (
        character_data["weapon"]["damage"] + character_data["attributes"]["strength"]
    )
    total_damage = base_damage

    # Apply character bonuses
    total_damage = apply_character_bonuses(
        character_data, monster, total_damage, turn, character_turns
    )

    # Apply monster vulnerabilities
    weapon_type = character_data["weapon"]["damage_type"]
    if monster.features:
        if "дробищему" in monster.features and weapon_type == "bludgeoning":
            total_damage *= 2
        elif "рубящему" in monster.features and weapon_type == "slashing":
            total_damage = 0  # No damage from slashing weapons

    log_entry = f"Ход {turn}: Персонаж атакует с силой {total_damage}."
    return total_damage, log_entry


def apply_character_bonuses(character_data, monster, damage, turn, character_turns):
    # Apply class-specific bonuses
    for class_name, level in character_data["class_levels"].items():
        if class_name.lower() == "разбойник" and level >= 1:
            # Rogue bonus: +1 damage if agility is higher
            if character_data["attributes"]["agility"] > monster.agility:
                damage += 1
                character_turns["rogue_bonus"] = True

        if class_name.lower() == "разбойник" and level >= 3:
            # Poison: +1 damage on second turn, +2 on third, etc.
            poison_damage = max(0, turn - 1)
            damage += poison_damage
            character_turns["poison"] = poison_damage

        if class_name.lower() == "воин" and level >= 1:
            # Warrior bonus: double damage on first turn
            if turn == 1:
                damage *= 2
                character_turns["warrior_first_strike"] = True

        if class_name.lower() == "варвар" and level >= 1:
            # Barbarian bonus: +2 damage for first 3 turns, then -1
            if turn <= 3:
                damage += 2
                character_turns["barbarian_rage"] = 2
            else:
                damage -= 1
                character_turns["barbarian_rage"] = -1

    return damage


def apply_defenses(character_data, monster, damage, turn, character_turns):
    # Apply character defenses
    for class_name, level in character_data["class_levels"].items():
        if class_name.lower() == "воин" and level >= 2:
            # Shield: -3 damage if character strength is higher than attacker's
            if character_data["attributes"]["strength"] > monster.strength:
                damage = max(0, damage - 3)
                character_turns["warrior_shield"] = True

        if class_name.lower() == "варвар" and level >= 2:
            # Stone skin: reduce damage by endurance
            damage = max(0, damage - character_data["attributes"]["endurance"])
            character_turns["barbarian_stone_skin"] = True

    return damage


def level_up_character(character_data, class_name):
    from .models import CharacterClass

    # Check if character can level up (max level is 3)
    if character_data["total_level"] >= 3:
        return character_data

    try:
        char_class = CharacterClass.objects.get(name__iexact=class_name)
    except CharacterClass.DoesNotExist:
        return character_data

    # Update class levels
    if class_name.lower() in character_data["class_levels"]:
        character_data["class_levels"][class_name.lower()] += 1
    else:
        character_data["class_levels"][class_name.lower()] = 1

    # Update total level
    character_data["total_level"] += 1

    # Recalculate max health
    character_data["max_health"] = calculate_max_health(character_data)
    character_data["health"] = character_data["max_health"]

    return character_data


def change_weapon(character_data, weapon):
    character_data["weapon"] = {
        "id": weapon.id,
        "name": weapon.name,
        "damage": weapon.damage,
        "damage_type": weapon.damage_type,
    }
    return character_data
