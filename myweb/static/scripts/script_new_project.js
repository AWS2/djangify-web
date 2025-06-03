document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('chat-form');
    const saveForm = document.getElementById('save-form');
    const input = document.getElementById('user-input');
    const box = document.querySelector('.chat-box');
    const visibleInput = document.getElementById('project-name-visible');
    const hiddenInput = document.getElementById('project-name-hidden');
    const saveButton = document.getElementById('save-btn');

    function toggleSaveButtonAndSync() {
        const value = visibleInput.value.trim();
        saveButton.disabled = value === '';
        hiddenInput.value = value;
    }

    visibleInput.addEventListener('input', toggleSaveButtonAndSync);
    toggleSaveButtonAndSync();

    // Envío del mensaje al asistente
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
        // 1) Mensaje del usuario
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.innerHTML = `<strong>Usuario:</strong> ${escapeHtml(data.user)}`;
        box.appendChild(userMsg);

        // 2) Mensaje del asistente
        const assistantMsg = document.createElement('div');
        assistantMsg.className = 'chat-message assistant';

        // Extraer el bloque crudo entre ``` ``` (sin procesar) y guardarlo en data-code
        const rawCodeMatch = data.assistant.match(/```(?:[\w\s#.-]*)?\n([\s\S]*?)```/i);
        const rawCode = rawCodeMatch ? rawCodeMatch[1] : '';
        assistantMsg.dataset.code = rawCode;
        console.log(data.assistant)

        // Mostrar el contenido formateado con marked
        assistantMsg.innerHTML = `<strong>Asistente:</strong> ${marked.parse(data.assistant)}`;
        box.appendChild(assistantMsg);

        input.value = '';
        box.scrollTop = box.scrollHeight;
    });
    });

    // Función para prevenir inyecciones en el mensaje del usuario
    function escapeHtml(text) {
    return text.replace(/[&<>"']/g, function (match) {
        const escapeMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
        };
        return escapeMap[match];
    });
    }

    // Al guardar proyecto, extraer el último bloque válido de models.py y admin.py
    saveForm.addEventListener('submit', function (e) {
        console.log('🟢 Entrando en saveForm submit');
        
        let modelsCode = '';
        let adminCode = '';

        const allMessages = document.querySelectorAll('.chat-message.assistant');

        allMessages.forEach(msg => {
            const code = msg.dataset.code;
            if (!code) return;

            // Solo analizamos bloques que contengan al menos 'admin.py'
            if (code.includes('# admin.py')) {
                const modelsMatch = code.match(/^([\s\S]*?)^\s*#\s*admin\.py\b/im);
                const adminMatch = code.match(/^#\s*admin\.py\b[\s\n]*([\s\S]*)$/im);

                modelsCode = modelsMatch ? modelsMatch[1].trim() : '';
                adminCode = adminMatch ? adminMatch[1].trim() : '';
            }
        });

        document.getElementById('models_code').value = modelsCode;
        document.getElementById('admin_code').value = adminCode;

        console.log('MODELS:\n', modelsCode);
        console.log('ADMIN:\n', adminCode);
    });
});