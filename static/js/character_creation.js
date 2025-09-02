// Game state for character creation
let characterCreationState = {
    selectedClassId: null,
    attributes: {
        strength: 0,
        agility: 0,
        endurance: 0
    }
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

// Initialize character creation
document.addEventListener('DOMContentLoaded', function () {
    initCharacterCreation();
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
            classList.innerHTML = ''; // Clear any existing content

            if (classes.length === 0) {
                showError('Нет доступных классов для создания персонажа');
                return;
            }

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
            classCards.forEach(card => {
                card.addEventListener('click', function () {
                    // Remove selected class from all cards
                    classCards.forEach(c => c.classList.remove('selected'));

                    // Add selected class to clicked card
                    this.classList.add('selected');

                    // Update selected class ID
                    characterCreationState.selectedClassId = this.dataset.classId;

                    // Update selected class display
                    document.getElementById('selected-class-name').textContent = this.querySelector('h4').textContent;

                    // Generate random attributes
                    generateRandomAttributes();

                    // Enable create button
                    document.getElementById('create-character').disabled = false;
                });
            });

            // Add event listener to create character button
            document.getElementById('create-character').addEventListener('click', function () {
                if (!characterCreationState.selectedClassId) {
                    showError('Пожалуйста, выберите класс');
                    return;
                }

                // Hide any previous errors
                hideError();

                // Disable button and show loading
                this.disabled = true;
                showLoading(true, 'Создание персонажа...');

                // Create character via API
                fetch(API_URLS.characterCreation, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify({
                        class_id: parseInt(characterCreationState.selectedClassId),
                        strength: characterCreationState.attributes.strength,
                        agility: characterCreationState.attributes.agility,
                        endurance: characterCreationState.attributes.endurance
                    })
                })
                .then(handleApiResponse)
                .then(data => {
                    if (data.error) {
                        showError('Ошибка: ' + data.error);
                        return;
                    }

                    // Redirect to battle page
                    window.location.href = '/battle/';
                })
                .catch(error => {
                    console.error('Error:', error);
                    showError('Ошибка при создании персонажа: ' + error.message);
                })
                .finally(() => {
                    // Re-enable button and hide loading
                    document.getElementById('create-character').disabled = false;
                    showLoading(false);
                });
            });

            // Add event listener to reroll attributes button
            document.getElementById('reroll-attributes').addEventListener('click', function() {
                if (!characterCreationState.selectedClassId) {
                    showError('Пожалуйста, выберите класс сначала');
                    return;
                }
                generateRandomAttributes();
            });

            // Hide loading
            showLoading(false);
        })
        .catch(error => {
            console.error('Error fetching classes:', error);
            showError('Ошибка при загрузке классов персонажей: ' + error.message);
            showLoading(false);
        });
}

// Generate random attributes (1-3)
function generateRandomAttributes() {
    characterCreationState.attributes.strength = Math.floor(Math.random() * 3) + 1;
    characterCreationState.attributes.agility = Math.floor(Math.random() * 3) + 1;
    characterCreationState.attributes.endurance = Math.floor(Math.random() * 3) + 1;

    // Update UI with random attributes
    document.getElementById('strength').textContent = characterCreationState.attributes.strength;
    document.getElementById('agility').textContent = characterCreationState.attributes.agility;
    document.getElementById('endurance').textContent = characterCreationState.attributes.endurance;
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