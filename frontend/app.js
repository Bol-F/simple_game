// app.js - vanilla JS client for Django REST API (Option A)
// Make sure your Django server runs at http://127.0.0.1:8000
const API_BASE = "http://127.0.0.1:8000"; // change if your Django uses different host/port

const $ = id => document.getElementById(id);

function log(msg) {
    const node = document.createElement("div");
    node.className = "log-row";
    node.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
    $("log").prepend(node);
}

async function apiFetch(path, opts = {}) {
    const url = path.startsWith("http") ? path : (API_BASE + path);
    try {
        if (opts.body && typeof opts.body === "object") {
            opts.headers = Object.assign({}, opts.headers, {"Content-Type": "application/json"});
            opts.body = JSON.stringify(opts.body);
        }
        const res = await fetch(url, opts);
        const text = await res.text();
        let data = null;
        try {
            data = text ? JSON.parse(text) : null;
        } catch (e) {
            data = text;
        }
        if (!res.ok) {
            const err = (data && data.detail) ? data.detail : (JSON.stringify(data) || res.statusText);
            throw new Error(err);
        }
        return data;
    } catch (err) {
        throw err;
    }
}

let currentChar = null;
let lastDrop = null;

function updateUI() {
    if (!currentChar) {
        $("char-json").textContent = "No character loaded";
        $("battle-btn").disabled = true;
        $("equip-btn").disabled = true;
        $("delete-btn").disabled = true;
        $("drop-info").textContent = "No drop";
        $("status").textContent = "";
        return;
    }

    // show character JSON (pretty)
    $("char-json").textContent = JSON.stringify(currentChar, null, 2);

    // enable/disable based on state
    $("battle-btn").disabled = !currentChar.is_alive;
    $("delete-btn").disabled = false;
    $("equip-btn").disabled = !(lastDrop && currentChar.is_alive);

    $("drop-info").textContent = lastDrop ? `Drop: ${lastDrop.name} (DMG ${lastDrop.damage})` : "No drop";

    if (!currentChar.is_alive) {
        $("status").textContent = "Character is dead. Create or load another.";
    } else if (currentChar.wins >= 5) {
        $("status").textContent = "🎉 You beat 5 monsters in a row! Game complete.";
        $("battle-btn").disabled = true;
    } else {
        $("status").textContent = `Wins in a row: ${currentChar.wins}`;
    }
}

async function createCharacter(evt) {
    evt.preventDefault();
    const name = $("name").value.trim();
    const char_class = $("char_class").value;
    if (!name) return log("Enter a name first");
    try {
        const data = await apiFetch("/characters/", {method: "POST", body: {name, char_class}});
        // DRF may return created object or serializer, accept both
        currentChar = data;
        lastDrop = null;
        updateUI();
        log(`Created ${data.name} (id=${data.id})`);
    } catch (err) {
        log("Create error: " + err.message);
    }
}

async function loadCharacter() {
    const id = $("load-id").value.trim();
    if (!id) return log("Enter ID to load");
    try {
        const data = await apiFetch(`/characters/${id}/`, {method: "GET"});
        currentChar = data;
        lastDrop = null;
        updateUI();
        log(`Loaded ${data.name}`);
    } catch (err) {
        log("Load error: " + err.message);
    }
}

async function startBattle() {
    if (!currentChar) return log("No character loaded");
    try {
        const data = await apiFetch(`/characters/${currentChar.id}/battle/`, {method: "POST"});
        // some implementations return { result, character, weapon_drop } while others return character directly
        const result = data.result || null;
        const drop = data.weapon_drop || data.drop || null;
        const charPart = data.character || data;

        if (charPart && typeof charPart === "object" && charPart.id === currentChar.id) {
            currentChar = charPart;
        } else if (charPart && charPart.id) {
            // safe fallback
            currentChar = charPart;
        }

        if (drop) {
            lastDrop = drop;
            log(`Battle result: ${result || 'unknown'}. Drop: ${drop.name} (DMG ${drop.damage})`);
        } else {
            lastDrop = null;
            log(`Battle result: ${result || 'unknown'}. No drop.`);
        }

        // update UI and detect final win condition
        if (currentChar.wins >= 5) {
            log("🎉 You have defeated 5 monsters in a row — game complete!");
        }

        updateUI();
    } catch (err) {
        log("Battle error: " + err.message);
    }
}

async function equipDrop() {
    if (!currentChar || !lastDrop) return log("No drop to equip");
    try {
        const data = await apiFetch(`/characters/${currentChar.id}/weapon/`, {
            method: "PUT",
            body: {weapon_id: lastDrop.id}
        });
        currentChar = data;
        log(`Equipped ${lastDrop.name}`);
        lastDrop = null;
        updateUI();
    } catch (err) {
        log("Equip error: " + err.message);
    }
}

async function deleteCharacter() {
    if (!currentChar) return log("No character loaded");
    if (!confirm("Delete this character?")) return;
    try {
        await apiFetch(`/characters/${currentChar.id}/`, {method: "DELETE"});
        log(`Deleted ${currentChar.name}`);
        currentChar = null;
        lastDrop = null;
        updateUI();
    } catch (err) {
        log("Delete error: " + err.message);
    }
}

/* Wire events after DOM ready */
document.addEventListener("DOMContentLoaded", () => {
    $("create-form").addEventListener("submit", createCharacter);
    $("load-btn").addEventListener("click", loadCharacter);
    $("battle-btn").addEventListener("click", startBattle);
    $("equip-btn").addEventListener("click", equipDrop);
    $("delete-btn").addEventListener("click", deleteCharacter);

    updateUI();
    log("UI ready. Create or load a character to start.");
});
