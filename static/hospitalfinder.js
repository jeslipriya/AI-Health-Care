function findHospitals() {
    const statusMessage = document.getElementById("statusMessage");
    const specializationDropdown = document.getElementById("specialization");
    let specialization = specializationDropdown.value;

    if (specialization === "custom") {
        specialization = document.getElementById("customSpecialization").value.trim();
        if (!specialization) {
            alert("Please enter a specialization.");
            return;
        }
    }

    statusMessage.innerText = "Getting your location...";

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;

            statusMessage.innerText = `Finding nearby ${specialization} hospitals...`;

            // OpenStreetMap Query
            const query = `
                [out:json];
                (
                    node["amenity"="hospital"](around:5000, ${lat}, ${lon});
                    node["healthcare:speciality"="${specialization.toLowerCase()}"](around:5000, ${lat}, ${lon});
                );
                out;
            `;

            const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    displayResults(data.elements, lat, lon, specialization);
                    statusMessage.innerText = `Here are the nearby ${specialization} hospitals:`;
                })
                .catch(error => {
                    console.error("Error fetching data:", error);
                    statusMessage.innerText = "Error finding hospitals. Try again.";
                });
        }, () => {
            statusMessage.innerText = "Location access denied.";
        });
    } else {
        statusMessage.innerText = "Geolocation is not supported by this browser.";
    }
}

function displayResults(places, userLat, userLon, specialization) {
    const placesList = document.getElementById("placesList");
    placesList.innerHTML = "";

    const map = L.map("map").setView([userLat, userLon], 13);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors"
    }).addTo(map);

    L.marker([userLat, userLon], { icon: L.icon({ iconUrl: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png" }) })
        .addTo(map)
        .bindPopup("You are here").openPopup();

    if (places.length === 0) {
        placesList.innerHTML = `<li>No ${specialization} hospitals found nearby.</li>`;
        return;
    }

    places.forEach(place => {
        if (place.lat && place.lon) {
            const listItem = document.createElement("li");
            listItem.textContent = place.tags.name || `Unnamed ${specialization} Hospital`;
            placesList.appendChild(listItem);

            L.marker([place.lat, place.lon], { icon: L.icon({ iconUrl: "https://maps.google.com/mapfiles/ms/icons/red-dot.png" }) })
                .addTo(map)
                .bindPopup(place.tags.name || `Unnamed ${specialization} Hospital`);
        }
    });
}