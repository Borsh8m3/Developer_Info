// Konfiguracja mapy i granic Polski
const polandBounds = L.latLngBounds([49.0, 14.1], [54.9, 24.1]);

const map = L.map('map', {
    maxBounds: polandBounds,
    maxBoundsViscosity: 1.0
}).setView([52.0, 19.1], 6);

L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png').addTo(map);

// Przykładowe dane do heatmapy [lat, lng, intensywność]
const heatData = [
    [52.23, 21.01, 1.0], // Warszawa
    [50.06, 19.94, 0.8], // Kraków
    [54.35, 18.64, 0.7], // Gdańsk
    [51.10, 17.03, 0.7], // Wrocław
    [52.40, 16.92, 0.6], // Poznań
    [53.42, 14.55, 0.4]  // Szczecin
];

L.heatLayer(heatData, {radius: 40, blur: 25, max: 1.0, gradient: {0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}}).addTo(map);

let selectedMarker = null;

map.on('click', function(e) {
    if (polandBounds.contains(e.latlng)) {
        if (selectedMarker) map.removeLayer(selectedMarker);
        selectedMarker = L.marker(e.latlng).addTo(map);
        window.currentCoords = e.latlng;
    } else {
        alert("Wybierz lokalizację w granicach Polski!");
    }
});

function updateRange(val) {
    document.getElementById('areaVal').innerText = val;
}

function openTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

function calculatePrice() {
    if (!window.currentCoords) {
        alert("Kliknij na mapę, aby wybrać lokalizację!");
        return;
    }

    const area = document.getElementById('area').value;
    const mkt = document.getElementById('market').value;
    const bld = document.getElementById('buildingType').value;
    const leg = document.getElementById('legalStatus').value;

    const distToWarsaw = map.distance(window.currentCoords, [52.23, 21.01]) / 1000;
    const locationFactor = Math.max(6000, 16000 - (distToWarsaw * 25)); 
    
    const finalPrice = area * locationFactor * mkt * bld * leg;

    document.getElementById('result').style.display = 'block';
    document.getElementById('priceDisplay').innerText = Math.round(finalPrice).toLocaleString() + " PLN";

    saveToHistory(area, finalPrice);
}

function saveToHistory(area, price) {
    const list = document.getElementById('historyList');
    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `<strong>${price.toLocaleString()} PLN</strong><br><small>${area} m² | ${new Date().toLocaleTimeString()}</small>`;
    list.prepend(div);
}

function clearHistory() {
    document.getElementById('historyList').innerHTML = "";
}