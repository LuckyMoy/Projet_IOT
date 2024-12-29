// Script pour gérer la navbar et le footer
fetch('layout/navbar.html')
.then(response => response.text())
.then(data => {
    document.getElementById('navbar').innerHTML = data;
        // Déterminer le nom de la page actuelle sans l'extension .html
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '');

        // Sélectionner le lien correspondant et ajouter la classe active
        const activeLink = document.getElementById(`navbar-link-${currentPage}`);
        if (activeLink) {
            activeLink.className = 'nav-link active';
        }
});

fetch('layout/footer.html')
.then(response => response.text())
.then(data => document.getElementById('footer').innerHTML = data);
