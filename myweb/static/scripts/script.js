function setLanguage(lang) {
    console.log("Cambiando idioma a:", lang);  // Para verificar que se llama la función
    const input = document.getElementById('language-input');
    input.value = lang;
    document.getElementById('language-form').submit();
}

document.addEventListener("DOMContentLoaded", function () {
    const deleteIcons = document.querySelectorAll('.delete-icon');

    deleteIcons.forEach(icon => {
        icon.addEventListener('click', async () => {
            const projectId = icon.dataset.id;
            const deleteUrl = icon.dataset.url;

            const confirmed = confirm("¿Estás seguro de que quieres eliminar este proyecto?");
            if (!confirmed) return;

            try {
                const response = await fetch(deleteUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('input[name="csrfmiddlewaretoken"]').value,
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    icon.closest('.project-container').remove();
                    alert("Proyecto borrado correctamente");
                    window.location.href=""
                } else {
                    throw new Error("No se pudo eliminar el proyecto.");
                }
            } catch (error) {
                console.error("Error:", error);
                alert("Hubo un problema al eliminar el proyecto.");
            }
        });
    });
});
