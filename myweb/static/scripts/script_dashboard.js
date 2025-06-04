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

    const modal = document.getElementById('changePasswordModal');
    const openBtn = document.getElementById('openChangePasswordBtn');
    const closeBtn = document.getElementById('closeModalBtn');

    openBtn.onclick = () => modal.style.display = 'block';
    closeBtn.onclick = () => modal.style.display = 'none';

    // Cerrar modal si clic fuera del contenido
    window.onclick = event => {
        if (event.target == modal) {
        modal.style.display = 'none';
        }
    };
});
