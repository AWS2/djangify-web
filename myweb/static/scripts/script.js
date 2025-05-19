function setLanguage(lang) {
    console.log("Cambiando idioma a:", lang);  // Para verificar que se llama la función
    const input = document.getElementById('language-input');
    input.value = lang;
    document.getElementById('language-form').submit();
}

