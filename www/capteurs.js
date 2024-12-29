// Script généré avec l'aide de chatGPT et de la documentation de charts.js

let plottedCapteurs = {}; // Object pour suivre les capteurs actuellement affichés
let yAxisMap = {}; // Associe chaque type de capteur à un axe Y unique

let plottedOnce = false;

// Charger les capteurs d'un logement
async function loadLogements() {
    try {
        const response = await fetch(`/api/logements`);
        if (!response.ok) throw new Error("Erreur lors du chargement des logements");
        const logements = await response.json();
        const tbody = document.getElementById("logements-table-body");

        logements.forEach(logement => {
            const row = document.createElement("tr");
            // adresse, tel, IP, date_insertion, lat, lon, nom, type
            row.innerHTML = `
                <td>${logement.type}</td>
                <td>${logement.nom}</td>
                <td>${logement.adresse}</td>
                <td>
                    <a href="/capteurs?adresse=${logement.adresse}&brut-data=${urlParams.get("brut-data")}">
                    <button class="btn btn-primary" id="choose-button-logement">
                        choisir
                    </button>
                    </a>
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error(error);
        alert("Impossible de charger les logements.");
    }
}

// Charger les capteurs d'un logement
async function loadCapteurs(adresse) {
    try {
        const response = adresse
            ? await fetch(`/api/capteurs?adresse=${encodeURIComponent(adresse)}`)
            : await fetch(`/api/capteurs`);
        if (!response.ok) throw new Error("Erreur lors du chargement des capteurs");
        const capteurs = await response.json();
        const tbody = document.getElementById("capteurs-table-body");

        capteurs.forEach(capteur => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${capteur.type}</td>
                <td>${capteur.ref_comm} (${capteur.id})</td>
                <td>${capteur.piece_nom} (${capteur.piece_id})</td>
                <td>${capteur.port}</td>
                <td>${capteur.date_insertion}</td>
                <td>${capteur.active? "actif": "inactif"}</td>
                <td>
                    <button class="btn btn-primary" id="ping-button-${capteur.id}" onclick="pingCapteur(${capteur.id}')">
                        Ping
                    </button>
                    <button class="btn btn-primary" id="plot-button-${capteur.id}" onclick="togglePlot(${capteur.id}, '${capteur.type}', '${capteur.piece_nom}')">
                        Add Plot
                    </button>
                    <span id="loading-${capteur.id}" class="spinner-border spinner-border-sm text-primary" style="display: none;" role="status"></span>
                    <span id="error-${capteur.id}" class="text-danger" style="display: none;">⚠</span>
                    <span id="nodata-${capteur.id}" class="text-warning" style="display: none;">no data</span>
                </td>
            `;
            tbody.appendChild(row);
        });

        // Afficher un graphique vide par défaut
        displayEmptyGraph();

        if(adresse != null && adresse != '') {
            document.getElementById("liste-capteurs").scrollIntoView({ behavior: "smooth", block: "center"});
        }
    } catch (error) {
        console.error(error);
        alert("Impossible de charger les capteurs.");
    }
}

// Fonction pour basculer entre `Plot` et `Unplot`
async function togglePlot(capteurId, capteurType, capteurPiece) {
    const button = document.getElementById(`plot-button-${capteurId}`);
    const loadingSpinner = document.getElementById(`loading-${capteurId}`);
    const errorSymbol = document.getElementById(`error-${capteurId}`);
    const nodataSymbol = document.getElementById(`nodata-${capteurId}`);

    // Si le capteur est déjà affiché, le retirer
    if (plottedCapteurs[capteurId]) {
        delete plottedCapteurs[capteurId];
        button.textContent = "Add Plot";
        updateGraph(); // Mettre à jour le graphique
        return;
    }

    // Afficher la roue de chargement
    loadingSpinner.style.display = "inline-block";
    errorSymbol.style.display = "none";
    nodataSymbol.style.display = "none";
    button.textContent = "Unplot";

    try {
        // Récupérer les filtres de période et de date
        const period = document.getElementById("period-select").value;
        const referenceDateInput = document.getElementById("reference-date").value;
        const referenceDate = referenceDateInput || new Date().toISOString().slice(0, 19).replace("T", " ");

        // Appel API pour récupérer les mesures
        const response = await fetch(`/api/mesures/${capteurId}?period=${period}&reference_date=${encodeURIComponent(referenceDate)}`);
        if (!response.ok && response.status == 404) nodataSymbol.style.display = "inline";
        if (!response.ok) throw new Error("Erreur lors du chargement des mesures");

        const mesures = await response.json();

        // Extraire les labels (dates) et les données (valeurs)
        const labels = mesures.map(m => new Date(m.d));
        const data = mesures.map(m => m.v);

        // Ajouter le capteur et ses données à `plottedCapteurs`
        plottedCapteurs[capteurId] = {
            labels,
            data,
            capteurType,
            capteurPiece
        };

        // Mettre à jour le graphique
        updateGraph();
        if(plottedOnce == false) {
            plottedOnce = true;
            document.getElementById("capteur-chart").scrollIntoView({ behavior: "smooth", block: "center" });
        }
    } catch (error) {
        console.error(error);
        errorSymbol.style.display = "inline";
        button.textContent = "Add Plot";
    } finally {
        // Masquer la roue de chargement
        loadingSpinner.style.display = "none";
    }
}

// Met à jour le graphique avec les capteurs sélectionnés
function updateGraph() {
    const chartCanvas = document.getElementById("capteur-chart");
    const datasets = [];
    const scales = { x: { type: 'time', title: { display: true, text: 'Temps' } } };

    const { dateStart, dateEnd } = getDateRange();
    scales.x.min = dateStart;
    scales.x.max = dateEnd;

    // Associer chaque type de capteur à un axe Y unique
    let yAxisIndex = 0;
    Object.keys(yAxisMap).forEach(key => delete yAxisMap[key]); // Réinitialiser le mappage

    // Construire les datasets et les axes Y
    for (const [capteurId, capteur] of Object.entries(plottedCapteurs)) {
        if (!yAxisMap[capteur.capteurType]) {
            const yAxisID = `y-${yAxisIndex++}`;
            yAxisMap[capteur.capteurType] = yAxisID;
            scales[yAxisID] = {
                type: "linear",
                position: yAxisIndex % 2 === 0 ? "left" : "right", // Alterner gauche/droite
                title: { display: true, text: capteur.capteurType }
            };
            if (capteur.capteurType === "Luminosité") {
                scales[yAxisID].type = "logarithmic";
            }
        }

        datasets.push({
            label: `${capteur.capteurType} (${capteur.capteurPiece})`,
            data: capteur.labels.map((label, index) => ({
                x: label,
                y: capteur.data[index]
            })),
            // borderColor: getRandomColor(),
            // backgroundColor: 'transparent',
            yAxisID: yAxisMap[capteur.capteurType],
            fill: false
        });
    }

    // Si aucun capteur n'est affiché, afficher un graphique vide
    if (datasets.length === 0) {
        displayEmptyGraph();
        return;
    }

    // Créer ou mettre à jour le graphique
    if (window.capteurChart) {
        window.capteurChart.destroy();
    }

    window.capteurChart = new Chart(chartCanvas, {
        type: 'line',
        data: { datasets },
        options: { responsive: true, scales }
    });

    if(urlParams.get('brut-data'))
        displayDatasetTable()
}

// Fonction pour afficher un graphique vide
function displayEmptyGraph() {
    const chartCanvas = document.getElementById("capteur-chart");
    document.getElementById("chart-title").textContent = "Graphique des mesures";
    document.getElementById("chart-title").style.display = "block";
    chartCanvas.style.display = "block";

    if (window.capteurChart) {
        window.capteurChart.destroy();
    }

    window.capteurChart = new Chart(chartCanvas, {
        type: 'line',
        data: { datasets: [] },
        options: { responsive: true, scales: { x: { type: 'time', title: { display: true, text: 'Temps' } } } }
    });

    plottedOnce = false;

    if(urlParams.get('brut-data'))
        displayDatasetTable()
}


// Fonction pour calculer la plage de dates
function getDateRange() {
    const period = document.getElementById("period-select").value;
    const referenceDateInput = document.getElementById("reference-date").value;
    const referenceDate = referenceDateInput ? new Date(referenceDateInput) : new Date();

    let dateStart;

    if (period === "1h") {
        dateStart = new Date(referenceDate.getTime() - 1 * 60 * 60 * 1000);
    } else if (period === "3h") {
        dateStart = new Date(referenceDate.getTime() - 3 * 60 * 60 * 1000);
    } else if (period === "12h") {
        dateStart = new Date(referenceDate.getTime() - 12 * 60 * 60 * 1000);
    } else if (!isNaN(parseInt(period))) {
        dateStart = new Date(referenceDate.getTime() - parseInt(period) * 24 * 60 * 60 * 1000);
    } else {
        dateStart = new Date(referenceDate);
    }

    return { dateStart, dateEnd: referenceDate };
}

let previousPeriod = document.getElementById("period-select").value;
let previousReferenceDate = document.getElementById("reference-date").value;

// Fonction pour mettre à jour les données des capteurs affichés
async function updateData() {
    const newPeriod = document.getElementById("period-select").value;
    const newReferenceDate = document.getElementById("reference-date").value;

    // Vérifie si la période a augmenté ou si la date de référence a changé
    if (newPeriod !== previousPeriod || newReferenceDate !== previousReferenceDate) {
        previousPeriod = newPeriod;
        previousReferenceDate = newReferenceDate;

        // Pour chaque capteur actuellement affiché, relance le GET pour récupérer les nouvelles données
        for (const capteurId of Object.keys(plottedCapteurs)) {
            const button = document.getElementById(`plot-button-${capteurId}`);
            const capteur = plottedCapteurs[capteurId];

            try {
                // Afficher la roue de chargement
                const loadingSpinner = document.getElementById(`loading-${capteurId}`);
                loadingSpinner.style.display = "inline-block";

                // Appel API pour récupérer les mesures avec la nouvelle période et date de référence
                const response = await fetch(`/api/mesures/${capteurId}?period=${newPeriod}&reference_date=${encodeURIComponent(newReferenceDate)}`);
                if (!response.ok) throw new Error("Erreur lors du chargement des mesures");

                const mesures = await response.json();

                // Mettre à jour les données du capteur
                plottedCapteurs[capteurId].labels = mesures.map(m => new Date(m.d));
                plottedCapteurs[capteurId].data = mesures.map(m => m.v);

            } catch (error) {
                console.error(`Erreur lors de la mise à jour des données pour le capteur ${capteurId}:`, error);
            } finally {
                // Masquer la roue de chargement
                const loadingSpinner = document.getElementById(`loading-${capteurId}`);
                loadingSpinner.style.display = "none";
            }
        }

        // Mettre à jour le graphique après avoir récupéré toutes les nouvelles données
        updateGraph();
    }
}

// Fonction pour afficher le tableau des données du dataset
function displayDatasetTable() {
    // Si le tableau existe déjà, le supprimer avant de le recréer
    const existingTableContainer = document.getElementById('dataset-table-container');
    if (existingTableContainer) {
        existingTableContainer.remove();
    }

    // Créer un conteneur pour le tableau
    const container = document.getElementById('brut-data-table');
    // container.id = 'dataset-table-container';
    // container.className = 'mt-4'; // Ajoute une marge en haut

    // Créer le tableau
    container.innerHTML = `
        <table id="dataset-table" class="table table-striped table-hover table-sm">
            <thead>
                <tr>
                    <th>Type</th>
                    <th>Pièce</th>
                    <th>Date</th>
                    <th>Valeur</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    `;

    const tbody = container.querySelector('tbody');

    // Ajouter les données des capteurs au tableau
    for(const [capteurId, capteur] of Object.entries(plottedCapteurs)) {
        capteur.labels.forEach((label, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${capteur.capteurType}</td>
                <td>${capteur.capteurPiece}</td>
                <td>${label.toLocaleString()}</td>
                <td>${capteur.data[index]}</td>
            `;
            tbody.appendChild(row);
        });
    }

    // Initialiser DataTables pour le tableau
    $('#dataset-table').DataTable({
        responsive: true,
        order: [[2, 'desc']], // Trier par date décroissante par défaut
        pageLength: 10,
        lengthMenu: [5, 10, 20, 50],
        language: {
            url: "/locales/fr_fr.json"
        }
    });
}


// Initialise l'heure actuelle par défaut pour le champ date
document.addEventListener("DOMContentLoaded", () => {
    const referenceDateInput = document.getElementById("reference-date");
    if (referenceDateInput) {
        const now = new Date();
        referenceDateInput.value = now.toISOString().slice(0, 19); // Format "YYYY-MM-DDTHH:MM:SS"
    }
});


// Relancer automatiquement `updateData` lors du changement de période ou de date de référence
document.getElementById("period-select").addEventListener("change", updateData);
document.getElementById("reference-date").addEventListener("change", updateData);

// Charger les capteurs pour un logement donné
const urlParams = new URLSearchParams(window.location.search);
const adresse = urlParams.get('adresse');
loadLogements();
loadCapteurs(adresse);

document.addEventListener('DOMContentLoaded', function () {
    const link = document.getElementById('disp-brut-data-link');
    const url = new URL(window.location.href);
    const isBrutData = url.searchParams.get('brut-data') === 'true';

    // Modifier le texte du lien au chargement de la page
    link.textContent = isBrutData ? 'Masquer donnée brute' : 'Donnée brute';

    // Ajouter l'événement click pour basculer l'état
    link.addEventListener('click', function (event) {
        event.preventDefault(); // Empêche le lien de suivre l'URL immédiatement

        // Met à jour le texte et le paramètre 'brut-data'
        url.searchParams.set('brut-data', isBrutData ? 'false' : 'true');
        window.location.href = url.toString(); // Redirige vers l'URL modifiée
    });
});
