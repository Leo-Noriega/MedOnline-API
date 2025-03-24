const offcanvas = document.getElementById('offcanvasScrolling');
const main = document.querySelector('main');

offcanvas.addEventListener('shown.bs.offcanvas', () => {
    if (window.innerWidth >= 992) {
        main.classList.add('shifted');
    }
});

offcanvas.addEventListener('hidden.bs.offcanvas', () => {
    if (window.innerWidth >= 992) {
        main.classList.remove('shifted');
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const links = document.querySelectorAll(".nav-link");

    function setActiveLink(link) {
        links.forEach(l => l.parentElement.classList.remove("active")); 
        link.parentElement.classList.add("active"); 
    }

    links.forEach(link => {
        link.addEventListener("click", function () {
            setActiveLink(this);
            localStorage.setItem("activeLink", this.href); 
        });
    });

    const activeLink = localStorage.getItem("activeLink");
    if (activeLink) {
        links.forEach(link => {
            if (link.href === activeLink) {
                setActiveLink(link);
            }
        });
    }
});