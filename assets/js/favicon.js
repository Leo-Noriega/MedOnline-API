document.addEventListener('DOMContentLoaded', () => {
    const favicon = document.getElementById('favicon');
    const setFavicon = () => {
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            favicon.href = "/assets/img/favicon/favicon-light-logo.png"; 
        } else {
            favicon.href = "/assets/img/favicon/favicon-dark-logo.png";
        }
    };
    setFavicon();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', setFavicon);
});