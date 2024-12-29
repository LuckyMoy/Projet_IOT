// Script généré avec l'aide de chatGPT

// Initialiser la carte
const map = L.map('map').setView([48.8566, 2.3522], 12); // Centré sur Paris par défaut

// Ajouter une couche de tuiles (carte de base)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fonction pour charger les logements depuis l'API ou la base de données
async function loadLogements() {
    try {
        const response = await fetch('/api/logements'); // Endpoint pour récupérer les logements
        if (!response.ok) throw new Error('Erreur lors du chargement des logements.');
        const logements = await response.json();

        // Ajouter un marqueur pour chaque logement
        logements.forEach(logement => {
            const { adresse, lat, lon, nom, type } = logement; // Assurez-vous que "nom" est une clé dans votre JSON
            const popupContent = `
                <div>
                    <a href="capteurs?adresse=${encodeURIComponent(adresse)}" style="font-weight: bold; text-decoration: none; color: #007bff;">
                        ${nom}
                    </a><br>
                    <span>${adresse}</span>
                </div>
            `;
            L.marker([lat, lon])
                .addTo(map)
                .bindPopup(popupContent);
        });

        // Ajuster la vue de la carte pour inclure tous les marqueurs
        const bounds = logements.map(logement => [logement.lat, logement.lon]);
        map.fitBounds(bounds);
    } catch (error) {
        console.error(error);
        alert('Impossible de charger les logements sur la carte.');
    }
}

// Charger les logements lorsque la page est prête
document.addEventListener('DOMContentLoaded', loadLogements);
