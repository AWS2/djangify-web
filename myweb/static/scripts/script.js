function setLanguage(lang) {
    console.log("Cambiando idioma a:", lang);  // Para verificar que se llama la función
    const input = document.getElementById('language-input');
    input.value = lang;
    document.getElementById('language-form').submit();
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('user-input');
    const box = document.querySelector('.chat-box');

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch(form.action || window.location.href, {
            method: "POST",
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ user_input: message })
        })
        .then(response => response.json())
        .then(data => {
            // Mensaje del usuario
            const userMsg = document.createElement('div');
            userMsg.className = 'chat-message user';
            userMsg.innerHTML = `<strong>Usuario:</strong> ${escapeHtml(data.user)}`;
            box.appendChild(userMsg);

            // Mensaje del asistente (formateado con markdown)
            const assistantMsg = document.createElement('div');
            assistantMsg.className = 'chat-message assistant';
            assistantMsg.innerHTML = `<strong>Asistente:</strong> ${marked.parse(data.assistant)}`;
            box.appendChild(assistantMsg);

            input.value = '';
            box.scrollTop = box.scrollHeight;
        });
    });

    // Función para evitar inyecciones
    function escapeHtml(text) {
        return text.replace(/[&<>"']/g, function (match) {
            const escapeMap = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return escapeMap[match];
        });
    }
});