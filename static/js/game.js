// Game state
let gameState = {
    character: null,
    monster: null,
    battleResult: null
};

// API endpoints
const API_URLS = {
    characterCreation: '/api/character/creation/',
    currentCharacter: '/api/character/current/',
    battle: '/api/battle/',
    levelUp: '/api/level-up/',
    weaponSelection: '/api/weapon-selection/'
};

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function () {
    // Character creation page
    if (document.querySelector('.character-creation')) {
        initCharacterCreation();
    }

    // Battle page
    if (document.querySelector('.battle')) {
        initBattle();
    }

    // Level up page
    if (document.querySelector('.level-up')) {
        initLevelUp();
    }

    // Weapon selection page
    if (document.querySelector('.weapon-selection')) {
        initWeaponSelection();
    }
});

// Character creation
function initCharacterCreation() {
    // First, fetch available classes from the API
    fetch(API_URLS.characterCreation)
        .then(response => response.json())
        .then(classes => {
            // Render classes in the UI
            const classList = document.querySelector('.class-list');
            classList.innerHTML = ''; // Clear any existing content

            classes.forEach(cls => {
                const classCard = document.createElement('div');
                classCard.className = 'class-card';
                classCard.dataset.classId = cls.id;
                classCard.innerHTML = `
                    <h4>${cls.name}</h4>
                    <p>Здоровье за уровень: ${cls.health_per_level}</p>
                    <p>Начальное оружие: ${cls.initial_weapon.name}</p>
                    <p>Бонус 1 уровня: ${cls.level1_bonus}</p>
                    <p>Бонус 2 уровня: ${cls.level2_bonus}</p>
                    <p>Бонус 3 уровня: ${cls.level3_bonus}</p>
                `;
                classList.appendChild(classCard);
            });

            // Add click event listeners to class cards
            const classCards = document.querySelectorAll('.class-card');
            let selectedClassId = null;

            classCards.forEach(card => {
                card.addEventListener('click', function () {
                    classCards.forEach(c => c.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedClassId = this.dataset.classId;
                });
            });

            // Add event listener to create character button
            document.getElementById('create-character').addEventListener('click', function () {
                if (!selectedClassId) {
                    alert('Пожалуйста, выберите класс');
                    return;
                }

                // Get random attributes (1-3)
                const strength = Math.floor(Math.random() * 3) + 1;
                const agility = Math.floor(Math.random() * 3) + 1;
                const endurance = Math.floor(Math.random() * 3) + 1;

                // Update UI with random attributes
                document.getElementById('strength').textContent = strength;
                document.getElementById('agility').textContent = agility;
                document.getElementById('endurance').textContent = endurance;

                // Create character via API
                fetch(API_URLS.characterCreation, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        class_id: selectedClassId,
                        strength: strength,
                        agility: agility,
                        endurance: endurance
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        gameState.character = data;
                        window.location.href = '/battle/';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Ошибка при создании персонажа');
                    });
            });
        })
        .catch(error => {
            console.error('Error fetching classes:', error);
            alert('Ошибка при загрузке классов персонажей');
        });
}

// Battle initialization
function initBattle() {
    // Load character data from the new endpoint
    fetch(API_URLS.currentCharacter)
        .then(response => {
            if (!response.ok) {
                throw new Error('No character found');
            }
            return response.json();
        })
        .then(data => {
            gameState.character = data;
            updateCharacterInfo();

            // Get a random monster
            return fetch(API_URLS.battle);
        })
        .then(response => response.json())
        .then(data => {
            gameState.monster = data;
            updateMonsterInfo();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Персонаж не найден. Создайте нового персонажа.');
            window.location.href = '/character-creation/';
        });

    // Start battle button
    document.getElementById('start-battle').addEventListener('click', startBattle);

    // Battle result buttons
    document.getElementById('level-up').addEventListener('click', goToLevelUp);
    document.getElementById('change-weapon').addEventListener('click', goToWeaponSelection);
    document.getElementById('continue').addEventListener('click', continueGame);
    document.getElementById('new-character').addEventListener('click', createNewCharacter);
}

function startBattle() {
    document.getElementById('start-battle').disabled = true;

    fetch(API_URLS.battle, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({monster_id: gameState.monster.id})
    })
        .then(response => response.json())
        .then(data => {
            gameState.battleResult = data;
            displayBattleLog(data.battle_log);

            // Update health displays
            document.getElementById('character-health').textContent = data.character_health;
            document.getElementById('monster-health').textContent = data.monster_health;

            // Show result
            const resultDiv = document.getElementById('battle-result');
            const resultMessage = document.getElementById('result-message');
            const victoryOptions = document.getElementById('victory-options');
            const defeatOptions = document.getElementById('defeat-options');

            resultDiv.classList.remove('hidden');

            if (data.result === 'win') {
                resultMessage.textContent = 'Победа!';
                resultMessage.className = 'victory';
                victoryOptions.classList.remove('hidden');
                defeatOptions.classList.add('hidden');

                // Store reward weapon for weapon selection
                if (data.reward_weapon) {
                    sessionStorage.setItem('reward_weapon', JSON.stringify(data.reward_weapon));
                }

                if (data.game_won) {
                    resultMessage.textContent = 'Поздравляем! Вы победили 5 монстров и прошли игру!';
                    // Redirect to victory page or show special message
                }
            } else {
                resultMessage.textContent = 'Поражение!';
                resultMessage.className = 'defeat';
                victoryOptions.classList.add('hidden');
                defeatOptions.classList.remove('hidden');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при запуске битвы');
            document.getElementById('start-battle').disabled = false;
        });
}

function displayBattleLog(log) {
    const logContainer = document.getElementById('log-container');
    logContainer.innerHTML = '';

    log.forEach(entry => {
        const p = document.createElement('p');
        p.textContent = entry;
        logContainer.appendChild(p);
    });

    logContainer.scrollTop = logContainer.scrollHeight;
}

function updateCharacterInfo() {
    if (!gameState.character) return;

    document.getElementById('character-level').textContent = gameState.character.total_level;
    document.getElementById('character-health').textContent = gameState.character.health;
    document.getElementById('character-max-health').textContent = gameState.character.max_health;
    document.getElementById('character-weapon').textContent = gameState.character.weapon.name;
}

function updateMonsterInfo() {
    if (!gameState.monster) return;

    document.getElementById('monster-name').textContent = gameState.monster.name;
    document.getElementById('monster-health').textContent = gameState.monster.health;
}

function goToLevelUp() {
    window.location.href = '/level-up/';
}

function goToWeaponSelection() {
    window.location.href = '/weapon-selection/';
}

function continueGame() {
    window.location.reload();
}

function createNewCharacter() {
    window.location.href = '/character-creation/';
}

// Level up page
function initLevelUp() {
    // Fetch available classes
    fetch(API_URLS.characterCreation)
        .then(response => response.json())
        .then(classes => {
            // Render classes in the UI
            const classList = document.querySelector('.class-list');
            classList.innerHTML = ''; // Clear any existing content

            classes.forEach(cls => {
                const classCard = document.createElement('div');
                classCard.className = 'class-card';
                classCard.dataset.className = cls.name;
                classCard.innerHTML = `
                    <h4>${cls.name}</h4>
                    <p>Здоровье за уровень: ${cls.health_per_level}</p>
                    <p>Бонус 1 уровня: ${cls.level1_bonus}</p>
                    <p>Бонус 2 уровня: ${cls.level2_bonus}</p>
                    <p>Бонус 3 уровня: ${cls.level3_bonus}</p>
                `;
                classList.appendChild(classCard);
            });

            // Add click event listeners to class cards
            const classCards = document.querySelectorAll('.class-card');
            let selectedClassName = null;

            classCards.forEach(card => {
                card.addEventListener('click', function () {
                    classCards.forEach(c => c.classList.remove('selected'));
                    this.classList.add('selected');
                    selectedClassName = this.dataset.className;
                });
            });

            // Add event listener to confirm button
            document.getElementById('confirm-level-up').addEventListener('click', function () {
                if (!selectedClassName) {
                    alert('Пожалуйста, выберите класс');
                    return;
                }

                fetch(API_URLS.levelUp, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({class_name: selectedClassName})
                })
                    .then(response => response.json())
                    .then(data => {
                        window.location.href = '/battle/';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('Ошибка при повышении уровня');
                    });
            });
        })
        .catch(error => {
            console.error('Error fetching classes:', error);
            alert('Ошибка при загрузке классов');
        });
}

// Weapon selection page
function initWeaponSelection() {
    // Load current character data
    fetch(API_URLS.characterCreation)
        .then(response => response.json())
        .then(character => {
            document.getElementById('current-weapon-name').textContent = character.weapon.name;
            document.getElementById('current-weapon-damage').textContent = `Урон: ${character.weapon.damage}`;
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при загрузке данных персонажа');
        });

    // Load new weapon from session storage
    const newWeapon = JSON.parse(sessionStorage.getItem('reward_weapon'));
    if (newWeapon) {
        document.getElementById('new-weapon-name').textContent = newWeapon.name;
        document.getElementById('new-weapon-damage').textContent = `Урон: ${newWeapon.damage}`;
    } else {
        alert('Новое оружие не найдено');
        window.location.href = '/battle/';
    }

    // Add event listeners to buttons
    document.getElementById('keep-weapon').addEventListener('click', function () {
        window.location.href = '/battle/';
    });

    document.getElementById('take-new-weapon').addEventListener('click', function () {
        fetch(API_URLS.weaponSelection, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({weapon_id: newWeapon.id})
        })
            .then(response => response.json())
            .then(data => {
                window.location.href = '/battle/';
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ошибка при смене оружия');
            });
    });
}

// Add this function to help with debugging
function debugLog(message, data = null) {
    console.log(`[DEBUG] ${message}`, data || '');
}

// In your character creation code, add debug logs:
document.getElementById('create-character').addEventListener('click', function () {
    debugLog('Create button clicked');
    debugLog('Selected class ID:', selectedClassId);

    if (!selectedClassId) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = 'Пожалуйста, выберите класс';
        errorDiv.classList.remove('hidden');
        return;
    }

    debugLog('Sending request to create character', {
        class_id: selectedClassId,
        strength: attributes.strength,
        agility: attributes.agility,
        endurance: attributes.endurance
    });

    // Create character via API
    fetch('/api/character/creation/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            class_id: selectedClassId,
            strength: attributes.strength,
            agility: attributes.agility,
            endurance: attributes.endurance
        })
    })
        .then(response => {
            debugLog('Response status:', response.status);
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            debugLog('Character created successfully:', data);
            if (data.error) {
                alert(data.error);
                return;
            }

            window.location.href = '/battle/';
        })
        .catch(error => {
            debugLog('Error creating character:', error);
            alert('Ошибка при создании персонажа: ' + error.message);
        });
});