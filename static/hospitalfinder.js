// Hospital Finder Application
class HospitalFinder {
    constructor() {
        this.statusMessage = document.getElementById("statusMessage");
        this.specializationDropdown = document.getElementById("specialization");
        this.placesList = document.getElementById("placesList");
        this.map = null;
        this.userMarker = null;
        this.hospitalMarkers = [];
        this.initEventListeners();
    }

    initEventListeners() {
        // Custom specialization toggle
        document.getElementById("specialization").addEventListener("change", () => {
            const customContainer = document.getElementById("customSpecializationContainer");
            customContainer.style.display = this.specializationDropdown.value === "custom" ? "block" : "none";
        });
    }

    async findHospitals() {
        try {
            const specialization = this.getSpecialization();
            if (!specialization) return;

            this.showStatus("Getting your location...", "info");

            const position = await this.getUserPosition();
            const { latitude: lat, longitude: lon } = position.coords;

            this.showStatus(`Finding nearby ${specialization} hospitals...`, "info");
            const hospitals = await this.fetchNearbyHospitals(lat, lon, specialization);

            this.displayResults(hospitals, lat, lon, specialization);
            this.showStatus(`Found ${hospitals.length} ${specialization} hospitals nearby`, "success");
        } catch (error) {
            console.error("Error in findHospitals:", error);
            this.showStatus(this.getErrorMessage(error), "error");
        }
    }

    getSpecialization() {
        let specialization = this.specializationDropdown.value;

        if (specialization === "custom") {
            specialization = document.getElementById("customSpecialization").value.trim();
            if (!specialization) {
                this.showStatus("Please enter a specialization", "error");
                return null;
            }
        }

        return specialization.toLowerCase();
    }

    getUserPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error("Geolocation is not supported by this browser."));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                resolve,
                (error) => reject(new Error(this.getGeolocationError(error))),
                { timeout: 10000, enableHighAccuracy: true }
            );
        });
    }

    getGeolocationError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                return "Location access denied. Please enable location services.";
            case error.POSITION_UNAVAILABLE:
                return "Location information is unavailable.";
            case error.TIMEOUT:
                return "The request to get user location timed out.";
            default:
                return "An unknown error occurred while getting your location.";
        }
    }

    async fetchNearbyHospitals(lat, lon, specialization) {
        // Overpass API query to find hospitals with optional specialization
        const query = specialization === "general" ? 
            `[out:json];
            (
                node["amenity"="hospital"](around:5000, ${lat}, ${lon});
                way["amenity"="hospital"](around:5000, ${lat}, ${lon});
                relation["amenity"="hospital"](around:5000, ${lat}, ${lon});
            );
            out center;` :
            `[out:json];
            (
                node["amenity"="hospital"]["healthcare:speciality"~"${specialization}",i](around:5000, ${lat}, ${lon});
                way["amenity"="hospital"]["healthcare:speciality"~"${specialization}",i](around:5000, ${lat}, ${lon});
                relation["amenity"="hospital"]["healthcare:speciality"~"${specialization}",i](around:5000, ${lat}, ${lon});
            );
            out center;`;

        const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            return data.elements || [];
        } catch (error) {
            console.error("Fetch error:", error);
            throw new Error("Failed to fetch hospital data. Please try again later.");
        }
    }

    displayResults(places, userLat, userLon, specialization) {
        this.clearPreviousResults();
        this.initMap(userLat, userLon);
        this.addUserMarker(userLat, userLon);

        if (places.length === 0) {
            this.placesList.innerHTML = `<li class="list-group-item">No ${specialization} hospitals found within 5km.</li>`;
            return;
        }

        // Sort by distance (closest first)
        places.sort((a, b) => {
            const distA = this.calculateDistance(userLat, userLon, a.lat || a.center.lat, a.lon || a.center.lon);
            const distB = this.calculateDistance(userLat, userLon, b.lat || b.center.lat, b.lon || b.center.lon);
            return distA - distB;
        });

        places.forEach(place => {
            const lat = place.lat || place.center.lat;
            const lon = place.lon || place.center.lon;
            const distance = this.calculateDistance(userLat, userLon, lat, lon);

            this.addHospitalToUI(place, distance, specialization);
            this.addHospitalToMap(place, lat, lon, specialization);
        });
    }

    clearPreviousResults() {
        this.placesList.innerHTML = "";
        if (this.map) {
            this.hospitalMarkers.forEach(marker => this.map.removeLayer(marker));
            this.hospitalMarkers = [];
        }
    }

    initMap(lat, lon) {
        if (!this.map) {
            this.map = L.map("map").setView([lat, lon], 14);
            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                maxZoom: 18
            }).addTo(this.map);
        } else {
            this.map.setView([lat, lon], 14);
        }
    }

    addUserMarker(lat, lon) {
        if (this.userMarker) {
            this.map.removeLayer(this.userMarker);
        }

        this.userMarker = L.marker([lat, lon], {
            icon: L.icon({
                iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png",
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            }),
            zIndexOffset: 1000
        }).addTo(this.map)
          .bindPopup("<b>Your Location</b>")
          .openPopup();
    }

    addHospitalToUI(place, distance, specialization) {
        const listItem = document.createElement("li");
        listItem.className = "list-group-item";

        const name = place.tags?.name || `Unnamed ${specialization} Hospital`;
        const address = place.tags?.["addr:full"] || place.tags?.["addr:street"] || "Address not available";
        const phone = place.tags?.phone ? `<a href="tel:${place.tags.phone}">${place.tags.phone}</a>` : "Phone not available";

        listItem.innerHTML = `
            <div class="hospital-info">
                <h5 class="mb-2">${name}</h5>
                <p class="mb-1"><strong>Address:</strong> ${address}</p>
                <p class="mb-1"><strong>Phone:</strong> ${phone}</p>
                <p class="mb-0"><strong>Distance:</strong> ${distance.toFixed(1)} km</p>
            </div>
        `;

        listItem.addEventListener("click", () => {
            const lat = place.lat || place.center.lat;
            const lon = place.lon || place.center.lon;
            this.map.setView([lat, lon], 16);
            this.hospitalMarkers.forEach(m => {
                if (m.getLatLng().lat === lat && m.getLatLng().lng === lon) {
                    m.openPopup();
                }
            });
        });

        this.placesList.appendChild(listItem);
    }

    addHospitalToMap(place, lat, lon, specialization) {
        const name = place.tags?.name || `Unnamed ${specialization} Hospital`;
        const address = place.tags?.["addr:full"] || place.tags?.["addr:street"] || "Address not available";
        const phone = place.tags?.phone || "Phone not available";

        const marker = L.marker([lat, lon], {
            icon: L.icon({
                iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34]
            })
        }).addTo(this.map)
          .bindPopup(`
              <b>${name}</b><br>
              ${address}<br>
              <strong>Phone:</strong> ${phone}
          `);

        this.hospitalMarkers.push(marker);
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        // Haversine formula to calculate distance in km
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    showStatus(message, type = "info") {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `text-${type}`;
    }

    getErrorMessage(error) {
        return error.message || "An unexpected error occurred. Please try again.";
    }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    const hospitalFinder = new HospitalFinder();
    
    // Make findHospitals available globally for the button onclick
    window.findHospitals = () => hospitalFinder.findHospitals();
});