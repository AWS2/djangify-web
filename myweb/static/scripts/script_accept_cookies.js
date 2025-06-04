function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = name + '=' + encodeURIComponent(value) + '; expires=' + expires + '; path=/';
}

function getCookie(name) {
    return document.cookie.split('; ').find(row => row.startsWith(name + '='))?.split('=')[1];
}

function acceptCookies() {
    setCookie('cookies_accepted', 'true', 365);
    document.getElementById('cookie-popup').style.display = 'none';
    enableProjectButton();
}

function denyCookies() {
    setCookie('cookies_accepted', 'false', 365);
    document.getElementById('cookie-popup').style.display = 'none';
}

function enableProjectButton() {
    const btn = document.getElementById('create-project-btn');
    if (btn) {
        btn.classList.remove('disabled');
        // Usar una URL absoluta o pasarla desde el HTML
        const dashboardUrl = btn.dataset.dashboardUrl || '/dashboard/';
        btn.setAttribute('href', dashboardUrl);
        btn.removeAttribute('tabindex');
        btn.style.cursor = 'pointer';
    }
}

window.onload = function() {
    const accepted = getCookie('cookies_accepted');
    if (!accepted) {
        document.getElementById('cookie-popup').style.display = 'block';
    } else if (accepted === 'true') {
        enableProjectButton();
    }
}