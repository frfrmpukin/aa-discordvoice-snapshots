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
            usernameSuggestions.innerHTML = "";
            return;
        }
        fetch(window.snapshotEditUserSearchUrl + "?q=" + encodeURIComponent(q))
            .then(r => r.json())
            .then(data => {
                usernameSuggestions.innerHTML = "";
                data.results.forEach(u => {
                    const item = document.createElement('button');
                    item.type = 'button';
                    item.className = 'list-group-item list-group-item-action';
                    item.textContent = u.username;
                    item.addEventListener('click', () => {
                        usernameInput.value = u.username;
                        usernameSuggestions.innerHTML = "";
                    });
                    usernameSuggestions.appendChild(item);
                });
            });
    }, 300));
}
