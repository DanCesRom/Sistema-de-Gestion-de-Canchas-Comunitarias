let map = L.map('map').setView([18.4861, -69.9312], 13); // default location

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);


// Add markers and click event to open side panel
// Add markers and click event to open side panel
const maxSmoothDistance = 40000; // 40 km in meters

// Crear el grupo de clusters
let markers = L.markerClusterGroup();

// Añadir marcadores al grupo en vez de directamente al mapa
places.forEach(place => {
    let marker = L.marker([place.latitude, place.longitude]);
    marker.on('click', () => {
        const targetLatLng = L.latLng(place.latitude, place.longitude);
        const currentLatLng = map.getCenter();
        const distance = currentLatLng.distanceTo(targetLatLng);

        if (distance < maxSmoothDistance) {
            map.flyTo(targetLatLng, 15, { duration: 2 });
        } else {
            map.setView(targetLatLng, 15);
        }

        openSidePanel(place);
    });

    markers.addLayer(marker);
});

// Añadir el grupo al mapa
map.addLayer(markers);

// Side panel elements
const sidePanel = document.getElementById("placeSidePanel");
const makeReservationBtn = document.getElementById("makeReservationBtn");



// Helper to format schedule nicely
function formatSchedule(place) {
    let days = place.open_days || "";
    let openTime = place.open_time || "";
    let closeTime = place.close_time || "";
    if (openTime && closeTime) {
        return `${days} ${openTime} - ${closeTime}`;
    }
    return days;
}


// Open side panel with place info Both Uses
function openSidePanel(place) {

    document.getElementById("placeImage").src = place.image_url || "";
    document.getElementById("placeName").textContent = place.name || "N/A";

    // Optional: map sport_type numeric to string if needed, or just show number
    document.getElementById("placeSportType").textContent = place.sport_type !== null && place.sport_type !== undefined ? place.sport_type : "N/A";
    document.getElementById("placeSchedule").textContent = formatSchedule(place);
    document.getElementById("placeDescription").textContent = place.description || "";


    // Update reservation button onclick
    makeReservationBtn.onclick = () => {
        window.location.href = `/reserve/${place.id}`;
    };


    // Show the panel with animation
    sidePanel.classList.add("show");
}

function closeSidePanel() {
    sidePanel.classList.remove("show");
}


// Click on map to close side panel (only if click is not on side panel itself)
map.on('click', function (e) {
    if (sidePanel.classList.contains('show')) {
        closeSidePanel();
    }
});

// Prevent clicks inside side panel from closing it
sidePanel.addEventListener('click', function (e) {
    e.stopPropagation();
});

// Navigation functions
function goToMap() { location.href = "/home"; }
function goToReservations() { location.href = "/reservations"; }
function goToSettings() { location.href = "/settings"; }
function goToHelp() { location.href = "/help"; }
function goToReservation(placeId) {
    location.href = `/reserve/${placeId}`;
}




// --- Autocomplete search dropdown ---

const searchInput = document.getElementById("searchBox");
const resultsDiv = document.getElementById("searchResults");

// --- Autocomplete search dropdown ---
function fetchSearchResults(query) {
    if (query.length < 2) {
        resultsDiv.style.display = "none";
        return;
    }

    fetch(`/api/search_places/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                resultsDiv.style.display = "none";
                return;
            }
            resultsDiv.innerHTML = "";
            data.forEach(place => {
                const div = document.createElement("div");
                div.style.padding = "8px";
                div.style.cursor = "pointer";
                div.style.borderBottom = "1px solid #eee";

                div.innerHTML = `<strong>${place.name}</strong><br/><small>Sport type: ${place.sport_type !== null && place.sport_type !== undefined ? place.sport_type : 'N/A'}</small>`;

                div.addEventListener("click", () => {
                    const targetLatLng = L.latLng(place.latitude, place.longitude);
                    const currentLatLng = map.getCenter();
                    const distance = currentLatLng.distanceTo(targetLatLng);
                    const maxSmoothDistance = 40000; // 40 km in meters

                    if (distance < maxSmoothDistance) {
                        map.flyTo(targetLatLng, 15, { duration: 2 });
                    } else {
                        map.setView(targetLatLng, 15);
                    }

                    openSidePanel(place);
                    resultsDiv.style.display = "none";
                    searchInput.value = place.name;
                });

                resultsDiv.appendChild(div);
            });
            resultsDiv.style.display = "block";
        })
        .catch(err => {
            console.error("Error fetching search results:", err);
            resultsDiv.style.display = "none";
        });


}

searchInput.addEventListener("input", function () {
    const query = this.value.trim();
    fetchSearchResults(query);
});


//  This makes it re-fetch on click if there's text
searchInput.addEventListener("focus", function () {
    const query = this.value.trim();
    if (query.length >= 2) {
        fetchSearchResults(query);
    }
});



// Optional: Hide dropdown if clicking outside
document.addEventListener("click", function (e) {
    if (!resultsDiv.contains(e.target) && e.target !== searchInput) {
        resultsDiv.style.display = "none";
    }
});






// Location button
let userMarker = null;
let accuracyCircle = null;

function goToMyLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;
                const accuracy = position.coords.accuracy; // accuracy in meters

                if (typeof map !== "undefined") {
                    map.setView([lat, lon], 16);

                    // Remove previous marker and circle if exist
                    if (userMarker) {
                        map.removeLayer(userMarker);
                    }
                    if (accuracyCircle) {
                        map.removeLayer(accuracyCircle);
                    }

                    // Add blue dot marker
                    userMarker = L.circleMarker([lat, lon], {
                        radius: 8,
                        fillColor: "#007bff",
                        color: "#ffffff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 1
                    }).addTo(map);

                    // Add accuracy circle
                    accuracyCircle = L.circle([lat, lon], {
                        radius: accuracy/2,
                        color: "#007bff",
                        fillColor: "#007bff",
                        fillOpacity: 0.2
                    }).addTo(map);

                } else {
                    alert("Map is not loaded.");
                }
            },
            function (error) {
                alert("Location access denied or unavailable.");
                console.error(error);
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}


