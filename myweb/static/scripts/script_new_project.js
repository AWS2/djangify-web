document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('chat-form');
    const saveForm = document.getElementById('save-form');
    const input = document.getElementById('user-input');
    const box = document.querySelector('.chat-box');
    const visibleInput = document.querySelectorAll('#project-name')[0];
    const hiddenInput = document.querySelectorAll('#project-name')[1];
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
    let modelsCode = '';
    let adminCode = '';
    const allMessages = document.querySelectorAll('.chat-message.assistant');

    allMessages.forEach(msg => {
        const code = msg.dataset.code;
        if (!code) return;

        const patterns = {
            models: [
                // Formato: **models.py** seguido de bloque Markdown
                /\*\*models\.py\*\*\s*```(?:python)?\s*([\s\S]*?)```/i,

                // Bloque Markdown con **models.py** dentro del código
                /```(?:python)?\s*\*\*models\.py\*\*\s*([\s\S]*?)```/i,

                // Formato simple: **models.py** seguido de código plano hasta **admin.py**
                /\*\*models\.py\*\*\s*([\s\S]*?)(?=\*\*admin\.py\*\*|\*\*\w+\.py\*\*|$)/i,

                // Formato inline dentro del ```python: # models.py (codigo)
                /```(?:python)?\s*#\s*models\.py.*?\n([\s\S]*?)(?=#\s*admin\.py|\*\*admin\.py\*\*|\*\*\w+\.py\*\*|$)/i
            ],
            admin: [
                // Formato: **admin.py** seguido de bloque Markdown
                /\*\*admin\.py\*\*\s*```(?:python)?\s*([\s\S]*?)```/i,

                // Bloque Markdown con **admin.py** dentro del código
                /```(?:python)?\s*\*\*admin\.py\*\*\s*([\s\S]*?)```/i,

                // Formato simple: **admin.py** seguido de código plano hasta otro bloque
                /\*\*admin\.py\*\*\s*([\s\S]*?)(?=\*\*\w+\.py\*\*|$)/i,

                // Formato inline dentro del ```python: # admin.py (codigo)
                /#\s*admin\.py.*?\n([\s\S]*?)```/i
            ]
        };

        function matchFirst(patterns, text) {
            for (const pattern of patterns) {
                const match = text.match(pattern);
                if (match) return match[1].trim();
            }
            return '';
        }

        modelsCode = matchFirst(patterns.models, code);
        adminCode = matchFirst(patterns.admin, code);
    });

    document.getElementById('models_code').value = modelsCode;
    document.getElementById('admin_code').value = adminCode;

    console.log("🟩 models.py:\n", modelsCode);
    console.log("🟦 admin.py:\n", adminCode);
    // El formulario se enviará automáticamente tras este evento
    });
});