function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// AA username autocomplete
const usernameInput = document.getElementById('username-input');
const usernameSuggestions = document.getElementById('username-suggestions');

if (usernameInput && usernameSuggestions) {
    usernameInput.addEventListener('input', debounce(function () {
        const q = this.value;
        if (!q) {
            usernameSuggestions.innerHTML = '';
            return;
        }
        fetch(window.snapshotEditUserSearchUrl + "?q=" + encodeURIComponent(q))
            .then(r => r.json())
            .then(data => {
                usernameSuggestions.innerHTML = '';
                data.results.forEach(u => {
                    const item = document.createElement('button');
                    item.type = 'button';
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = u.username;
                    item.addEventListener('click', () => {
                        usernameInput.value = u.username;
                        usernameSuggestions.innerHTML = '';
                    });
                    usernameSuggestions.appendChild(item);
                });
            });
    }, 300));
}

// Discord username autocomplete
const discordInput = document.getElementById('discord-input');
const discordSuggestions = document.getElementById('discord-suggestions');

if (discordInput && discordSuggestions) {
    discordInput.addEventListener('input', debounce(function () {
        const q = this.value;
        if (!q) {
            discordSuggestions.innerHTML = '';
            return;
        }
        fetch(window.snapshotEditDiscordSearchUrl + "?q=" + encodeURIComponent(q))
            .then(r => r.json())
            .then(data => {
                discordSuggestions.innerHTML = '';
                data.results.forEach(u => {
                    const item = document.createElement('button');
                    item.type = 'button';
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = u.discord_username + " (AA: " + u.aa_username + ")";
                    item.addEventListener('click', () => {
                        discordInput.value = u.discord_username;
                        discordSuggestions.innerHTML = '';
                    });
                    discordSuggestions.appendChild(item);
                });
            });
    }, 300));
}
