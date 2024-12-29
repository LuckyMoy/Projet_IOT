// Mapper les descriptions météo aux images correspondantes
const weatherIcons = {
    rain: "img/rain.png",
    clouds: "img/cloud.png",
    snow: "img/snow.png",
    clear: "img/sun.png",
    thunderstorm: "img/thunder.png",
    wind: "img/wind.png"
};

// Fonction pour charger les prévisions météo
// Source GPT
async function loadWeather(city = "Paris") {
    try {
        const response = await fetch(`/api/weather-json?city=${city}`);
        if (!response.ok) throw new Error("Impossible de charger les données météo.");
        const data = await response.json();

        // Construire le HTML pour les prévisions météo
        const weatherCarousel = document.getElementById("weather-carousel");
        weatherCarousel.innerHTML = data.list.map(item => {
            const dateTime = new Date(item.dt_txt);
            const date = dateTime.toLocaleDateString("fr-FR", {
                weekday: "short",
                day: "numeric",
                month: "short"
            });
            const time = dateTime.toLocaleTimeString("fr-FR", {
                hour: "2-digit",
                minute: "2-digit"
            });
            const temp = Math.round(item.main.temp);
            const description = item.weather[0].main.toLowerCase();
            const icon = weatherIcons[description] || "img/cloud.png";

            return `
                <div class="weather-card">
                    <img src="${icon}" alt="${description}">
                    <h5>${date}</h5>
                    <p>${time}</p>
                    <p>${temp}°C</p>
                    <p>${item.weather[0].description}</p>
                </div>
            `;
        }).join("");
    } catch (error) {
        console.error(error);
        document.getElementById("weather-carousel").innerHTML = `<p class="text-danger">Erreur : Impossible de récupérer les données météo.</p>`;
    }
}

// Fonction pour défiler horizontalement dans le carrousel
// Source GPT
function scrollCarousel(direction) {
    const carousel = document.getElementById("weather-carousel");
    const scrollAmount = 200; // Largeur d'un élément + marges
    carousel.scrollBy({
        left: direction * scrollAmount,
        behavior: "smooth"
    });
}

// Charger les prévisions météo au chargement de la page
document.addEventListener("DOMContentLoaded", () => loadWeather());
