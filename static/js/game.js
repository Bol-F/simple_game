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

// Enhanced response handler to detect HTML responses
function handleApiResponse(response) {
    const contentType = response.headers.get('content-type');

    // Check if response is JSON
    if (contentType && contentType.includes('application/json')) {
        return response.json().then(data => {
            if (!response.ok) {
                throw new Error(data.error || `Server error: ${response.status}`);
            }
            return data;
        });
    }
    // Handle HTML responses (errors)
    else {
        return response.text().then(text => {
            // Try to extract error message from HTML
            const errorMatch = text.match(/<title[^>]*>([^<]+)<\/title>/i) ||
                              text.match(/<h1[^>]*>([^<]+)<\/h1>/i);

            if (errorMatch && errorMatch[1]) {
                throw new Error(`Server error: ${errorMatch[1]}`);
            } else {
                throw new Error('Server returned HTML instead of JSON. Please check the API endpoint.');
            }
        });
    }
}

// Initialize the game
document.addEventListener('DOMContentLoaded', function () {
    // Check if we're on the battle page
    if (window.location.pathname === '/battle/' || document.querySelector('.battle')) {
        initBattle();
    }

    // Character creation page
    if (document.querySelector('.character-creation')) {
        initCharacterCreation();
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
    // Show loading state
    showLoading(true, 'Загрузка классов...');

    // First, fetch available classes from the API
    fetch(API_URLS.characterCreation)
        .then(handleApiResponse)
        .then(classes => {
            // Render classes in the UI
            const classList = document.querySelector('.class-list');
            if (classList) {
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
                        <p>Бonус 3 уровня: ${cls.level3_bonus}</p>
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

                        // Update selected class display
                        const selectedClassElement = document.getElementById('selected-class');
                        if (selectedClassElement) {
                            selectedClassElement.textContent = this.querySelector('h4').textContent;
                        }
                    });
                });

                // Add event listener to create character button
                const createButton = document.getElementById('create-character');
                if (createButton) {
                    createButton.addEventListener('click', function () {
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

                        // Show loading
                        showLoading(true, 'Создание персонажа...');

                        // Create character via API
                        fetch(API_URLS.characterCreation, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({
                                class_id: parseInt(selectedClassId),
                                strength: strength,
                                agility: agility,
                                endurance: endurance
                            })
                        })
                        .then(handleApiResponse)
                        .then(data => {
                            gameState.character = data;
                            window.location.href = '/battle/';
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Ошибка при создании персонажа: ' + error.message);
                        })
                        .finally(() => {
                            showLoading(false);
                        });
                    });
                }
            }

            // Hide loading
            showLoading(false);
        })
        .catch(error => {
            console.error('Error fetching classes:', error);
            alert('Ошибка при загрузке классов персонажей: ' + error.message);
            showLoading(false);
        });
}

// Battle initialization
function initBattle() {
    console.log('Initializing battle page');

    // Show loading
    showLoading(true, 'Загрузка персонажа...');

    // Load character data from the new endpoint
    fetch(API_URLS.currentCharacter)
        .then(handleApiResponse)
        .then(data => {
            gameState.character = data;
            updateCharacterInfo();

            // Get a random monster
            return fetch(API_URLS.battle);
        })
        .then(handleApiResponse)
        .then(data => {
            gameState.monster = data;
            updateMonsterInfo();
            showLoading(false);

            // Add event listeners after content is loaded
            const startBattleButton = document.getElementById('start-battle');
            if (startBattleButton) {
                startBattleButton.addEventListener('click', startBattle);
            }

            const levelUpButton = document.getElementById('level-up');
            if (levelUpButton) {
                levelUpButton.addEventListener('click', goToLevelUp);
            }

            const changeWeaponButton = document.getElementById('change-weapon');
            if (changeWeaponButton) {
                changeWeaponButton.addEventListener('click', goToWeaponSelection);
            }

            const continueButton = document.getElementById('continue');
            if (continueButton) {
                continueButton.addEventListener('click', continueGame);
            }

            const newCharacterButton = document.getElementById('new-character');
            if (newCharacterButton) {
                newCharacterButton.addEventListener('click', createNewCharacter);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Персонаж не найден. Создайте нового персонажа: ' + error.message);
            window.location.href = '/character-creation/';
            showLoading(false);
        });
}

function startBattle() {
    const startButton = document.getElementById('start-battle');
    if (startButton) {
        startButton.disabled = true;
    }

    showLoading(true, 'Начало битвы...');

    fetch(API_URLS.battle, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({monster_id: gameState.monster.id})
    })
    .then(handleApiResponse)
    .then(data => {
        gameState.battleResult = data;
        displayBattleLog(data.battle_log);

        // Update health displays
        document.getElementById('character-health').textContent = data.character_health;
        document.getElementById('monster-health').textContent = data.monster_health;

        // Update health bars
        updateHealthBars();

        // Show result
        const resultDiv = document.getElementById('battle-result');
        const resultMessage = document.getElementById('result-message');
        const victoryOptions = document.getElementById('victory-options');
        const defeatOptions = document.getElementById('defeat-options');

        if (resultDiv && resultMessage && victoryOptions && defeatOptions) {
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
                }
            } else {
                resultMessage.textContent = 'Поражение!';
                resultMessage.className = 'defeat';
                victoryOptions.classList.add('hidden');
                defeatOptions.classList.remove('hidden');
            }
        }

        showLoading(false);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ошибка при запуске битвы: ' + error.message);

        const startButton = document.getElementById('start-battle');
        if (startButton) {
            startButton.disabled = false;
        }

        showLoading(false);
    });
}

function displayBattleLog(log) {
    const logContainer = document.getElementById('log-container');
    if (logContainer) {
        logContainer.innerHTML = '';

        log.forEach(entry => {
            const p = document.createElement('p');
            p.textContent = entry;
            logContainer.appendChild(p);
        });

        logContainer.scrollTop = logContainer.scrollHeight;
    }
}

function updateCharacterInfo() {
    if (!gameState.character) return;

    const levelElement = document.getElementById('character-level');
    const healthElement = document.getElementById('character-health');
    const maxHealthElement = document.getElementById('character-max-health');
    const weaponElement = document.getElementById('character-weapon');

    if (levelElement) levelElement.textContent = gameState.character.total_level;
    if (healthElement) healthElement.textContent = gameState.character.health;
    if (maxHealthElement) maxHealthElement.textContent = gameState.character.max_health;
    if (weaponElement) weaponElement.textContent = gameState.character.weapon.name;

    // Update health bar
    updateHealthBars();
}

function updateMonsterInfo() {
    if (!gameState.monster) return;

    const nameElement = document.getElementById('monster-name');
    const healthElement = document.getElementById('monster-health');

    if (nameElement) nameElement.textContent = gameState.monster.name;
    if (healthElement) healthElement.textContent = gameState.monster.health;

    // Update health bar
    updateHealthBars();
}

function updateHealthBars() {
    // Update character health bar
    if (gameState.character) {
        const characterHealthPercent = (gameState.character.health / gameState.character.max_health) * 100;
        const characterHealthFill = document.getElementById('character-health-fill');
        if (characterHealthFill) {
            characterHealthFill.style.width = `${characterHealthPercent}%`;
        }
    }

    // Update monster health bar
    if (gameState.monster) {
        const monsterHealthPercent = (gameState.monster.health / gameState.monster.health) * 100;
        const monsterHealthFill = document.getElementById('monster-health-fill');
        if (monsterHealthFill) {
            monsterHealthFill.style.width = `${monsterHealthPercent}%`;
        }
    }
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
    // Show loading
    showLoading(true, 'Загрузка классов...');

    // Fetch available classes
    fetch(API_URLS.characterCreation)
        .then(handleApiResponse)
        .then(classes => {
            // Render classes in the UI
            const classList = document.querySelector('.class-list');
            if (classList) {
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
                const confirmButton = document.getElementById('confirm-level-up');
                if (confirmButton) {
                    confirmButton.addEventListener('click', function () {
                        if (!selectedClassName) {
                            alert('Пожалуйста, выберите класс');
                            return;
                        }

                        // Show loading
                        showLoading(true, 'Повышение уровня...');

                        fetch(API_URLS.levelUp, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            },
                            body: JSON.stringify({class_name: selectedClassName})
                        })
                        .then(handleApiResponse)
                        .then(data => {
                            window.location.href = '/battle/';
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('Ошибка при повышении уровня: ' + error.message);
                        })
                        .finally(() => {
                            showLoading(false);
                        });
                    });
                }
            }

            // Hide loading
            showLoading(false);
        })
        .catch(error => {
            console.error('Error fetching classes:', error);
            alert('Ошибка при загрузке классов: ' + error.message);
            showLoading(false);
        });
}

// Weapon selection page
function initWeaponSelection() {
    // Show loading
    showLoading(true, 'Загрузка данных...');

    // Load current character data
    fetch(API_URLS.currentCharacter)
        .then(handleApiResponse)
        .then(character => {
            document.getElementById('current-weapon-name').textContent = character.weapon.name;
            document.getElementById('current-weapon-damage').textContent = `Урон: ${character.weapon.damage}`;

            // Load new weapon from session storage
            const newWeapon = JSON.parse(sessionStorage.getItem('reward_weapon'));
            if (newWeapon) {
                document.getElementById('new-weapon-name').textContent = newWeapon.name;
                document.getElementById('new-weapon-damage').textContent = `Урон: ${newWeapon.damage}`;
            } else {
                alert('Новое оружие не найдено');
                window.location.href = '/battle/';
                return;
            }

            // Hide loading
            showLoading(false);

            // Add event listeners to buttons
            document.getElementById('keep-weapon').addEventListener('click', function () {
                window.location.href = '/battle/';
            });

            document.getElementById('take-new-weapon').addEventListener('click', function () {
                // Show loading
                showLoading(true, 'Смена оружия...');

                fetch(API_URLS.weaponSelection, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({weapon_id: newWeapon.id})
                })
                .then(handleApiResponse)
                .then(data => {
                    window.location.href = '/battle/';
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Ошибка при смене оружия: ' + error.message);
                })
                .finally(() => {
                    showLoading(false);
                });
            });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ошибка при загрузке данных персонажа: ' + error.message);
            showLoading(false);
        });
}

// Utility functions for UI feedback
function showError(message) {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.style.display = 'block';

        // Auto-hide error after 5 seconds
        setTimeout(() => {
            hideError();
        }, 5000);
    } else {
        alert(message);
    }
}

function hideError() {
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
        errorElement.style.display = 'none';
    }
}

function showLoading(show, message = 'Загрузка...') {
    const loadingElement = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');

    if (loadingElement && loadingText) {
        if (show) {
            loadingText.textContent = message;
            loadingElement.style.display = 'block';
        } else {
            loadingElement.style.display = 'none';
        }
    }
}

// Debug function
function debugLog(message, data = null) {
    console.log(`[DEBUG] ${message}`, data || '');
}