/**
 * JavaScript for Hospital Location finder
 */

document.addEventListener('DOMContentLoaded', function() {
    const map = L.map('map');
    const locateButton = document.getElementById('locate-me');
    const hospitalsList = document.getElementById('hospitals-list');
    const searchInput = document.getElementById('location-search');
    const searchButton = document.getElementById('search-location');
    
    // Set default view to a generic location
    map.setView([40.7128, -74.0060], 13);
    
    // Add OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Variables to store markers
    let userMarker = null;
    const hospitalMarkers = [];
    
    // Initialize error container
    const errorContainer = document.createElement('div');
    errorContainer.classList.add('alert', 'alert-danger', 'd-none', 'mt-3');
    document.querySelector('.map-container').appendChild(errorContainer);
    
    // Function to show error
    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('d-none');
        setTimeout(() => {
            errorContainer.classList.add('d-none');
        }, 5000);
    }
    
    // Event listener for locate button
    if (locateButton) {
        locateButton.addEventListener('click', getUserLocation);
    }
    
    // Event listener for search button
    if (searchButton && searchInput) {
        searchButton.addEventListener('click', function() {
            const location = searchInput.value.trim();
            if (location) {
                geocodeLocation(location);
            }
        });
        
        // Search on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const location = searchInput.value.trim();
                if (location) {
                    geocodeLocation(location);
                }
            }
        });
    }
    
    /**
     * Get user's current location
     */
    function getUserLocation() {
        if (!navigator.geolocation) {
            showError('Geolocation is not supported by your browser');
            return;
        }
        
        // Show loading indicator
        if (locateButton) {
            showSpinner(locateButton, 'sm');
        }
        
        navigator.geolocation.getCurrentPosition(
            function(position) {
                // Hide loading indicator
                if (locateButton) {
                    hideSpinner(locateButton);
                }
                
                const userLat = position.coords.latitude;
                const userLng = position.coords.longitude;
                
                // Update map with user location
                updateUserLocation(userLat, userLng);
                
                // Find hospitals near the location
                findNearbyHospitals(userLat, userLng);
            },
            function(error) {
                // Hide loading indicator
                if (locateButton) {
                    hideSpinner(locateButton);
                }
                
                let errorMsg;
                switch(error.code) {
                    case error.PERMISSION_DENIED:
                        errorMsg = 'User denied the request for Geolocation.';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        errorMsg = 'Location information is unavailable.';
                        break;
                    case error.TIMEOUT:
                        errorMsg = 'The request to get user location timed out.';
                        break;
                    default:
                        errorMsg = 'An unknown error occurred.';
                        break;
                }
                showError(errorMsg);
            }
        );
    }
    
    /**
     * Geocode a location string to coordinates
     * @param {string} location - Location string to geocode
     */
    function geocodeLocation(location) {
        // Show loading indicator
        if (searchButton) {
            showSpinner(searchButton, 'sm');
        }
        
        // Use Nominatim for geocoding (OpenStreetMap)
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                if (searchButton) {
                    hideSpinner(searchButton);
                }
                
                if (data && data.length > 0) {
                    const lat = parseFloat(data[0].lat);
                    const lng = parseFloat(data[0].lon);
                    
                    // Update map with location
                    updateUserLocation(lat, lng);
                    
                    // Find hospitals near the location
                    findNearbyHospitals(lat, lng);
                } else {
                    showError('Location not found. Please try a different search term.');
                }
            })
            .catch(error => {
                // Hide loading indicator
                if (searchButton) {
                    hideSpinner(searchButton);
                }
                
                console.error('Geocoding error:', error);
                showError('Error finding location. Please try again.');
            });
    }
    
    /**
     * Update user location on map
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     */
    function updateUserLocation(lat, lng) {
        // If marker already exists, remove it
        if (userMarker) {
            map.removeLayer(userMarker);
        }
        
        // Create new marker for user location
        const userIcon = L.divIcon({
            html: '<i class="fas fa-user-circle" style="color: #007bff; font-size: 24px;"></i>',
            className: 'user-location-marker',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        userMarker = L.marker([lat, lng], { icon: userIcon }).addTo(map);
        userMarker.bindPopup('Your Location').openPopup();
        
        // Center map on user location
        map.setView([lat, lng], 13);
    }
    
    /**
     * Find hospitals near a location
     * @param {number} lat - Latitude
     * @param {number} lng - Longitude
     */
    function findNearbyHospitals(lat, lng) {
        // Show loading indicator in hospitals list
        if (hospitalsList) {
            hospitalsList.innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        }
        
        // Remove existing hospital markers
        hospitalMarkers.forEach(marker => {
            map.removeLayer(marker);
        });
        hospitalMarkers.length = 0;
        
        // Use Overpass API to find hospitals
        const radius = 5000; // 5km radius
        const query = `
            [out:json];
            (
              node["amenity"="hospital"](around:${radius},${lat},${lng});
              way["amenity"="hospital"](around:${radius},${lat},${lng});
              relation["amenity"="hospital"](around:${radius},${lat},${lng});
            );
            out center;
        `;
        
        const url = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(query)}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const hospitals = [];
                
                // Process results
                data.elements.forEach(element => {
                    let hospitalLat, hospitalLng, name;
                    
                    if (element.type === 'node') {
                        hospitalLat = element.lat;
                        hospitalLng = element.lon;
                    } else if (element.center) {
                        hospitalLat = element.center.lat;
                        hospitalLng = element.center.lon;
                    } else {
                        return; // Skip if no coordinates
                    }
                    
                    name = element.tags ? (element.tags.name || 'Unnamed Hospital') : 'Unnamed Hospital';
                    
                    // Calculate distance from user
                    const distance = calculateDistance(lat, lng, hospitalLat, hospitalLng);
                    
                    hospitals.push({
                        name: name,
                        lat: hospitalLat,
                        lng: hospitalLng,
                        distance: distance,
                        phone: element.tags ? element.tags.phone : null,
                        emergency: element.tags ? element.tags.emergency : null
                    });
                });
                
                // Sort by distance
                hospitals.sort((a, b) => a.distance - b.distance);
                
                // Display on map and in list
                displayHospitals(hospitals);
            })
            .catch(error => {
                console.error('Hospital search error:', error);
                if (hospitalsList) {
                    hospitalsList.innerHTML = '<div class="alert alert-danger">Error finding hospitals. Please try again.</div>';
                }
            });
    }
    
    /**
     * Display hospitals on map and in list
     * @param {Array} hospitals - Array of hospital objects
     */
    function displayHospitals(hospitals) {
        // Clear hospitals list
        if (hospitalsList) {
            hospitalsList.innerHTML = '';
        }
        
        if (hospitals.length === 0) {
            if (hospitalsList) {
                hospitalsList.innerHTML = '<div class="alert alert-info">No hospitals found in this area. Try expanding your search.</div>';
            }
            return;
        }
        
        // Create hospital icon
        const hospitalIcon = L.divIcon({
            html: '<i class="fas fa-hospital-alt" style="color: #dc3545; font-size: 24px;"></i>',
            className: 'hospital-marker',
            iconSize: [24, 24],
            iconAnchor: [12, 12]
        });
        
        // Add hospitals to map and list
        hospitals.forEach((hospital, index) => {
            // Add marker to map
            const marker = L.marker([hospital.lat, hospital.lng], { icon: hospitalIcon }).addTo(map);
            marker.bindPopup(`<strong>${hospital.name}</strong><br>Distance: ${hospital.distance.toFixed(1)} km`);
            hospitalMarkers.push(marker);
            
            // Add to list
            if (hospitalsList) {
                const card = document.createElement('div');
                card.classList.add('card', 'mb-3', 'hospital-card');
                
                let emergencyBadge = '';
                if (hospital.emergency === 'yes') {
                    emergencyBadge = '<span class="badge bg-danger ms-2">Emergency</span>';
                }
                
                let phoneInfo = '';
                if (hospital.phone) {
                    phoneInfo = `<p class="card-text"><i class="fas fa-phone-alt me-2"></i>${hospital.phone}</p>`;
                }
                
                card.innerHTML = `
                    <div class="card-body">
                        <h5 class="card-title">${hospital.name} ${emergencyBadge}</h5>
                        <p class="card-text"><i class="fas fa-map-marker-alt me-2"></i>Distance: ${hospital.distance.toFixed(1)} km</p>
                        ${phoneInfo}
                        <button class="btn btn-sm btn-outline-primary show-on-map" data-index="${index}">Show on Map</button>
                    </div>
                `;
                
                hospitalsList.appendChild(card);
                
                // Add event listener to show on map button
                card.querySelector('.show-on-map').addEventListener('click', function() {
                    const index = parseInt(this.getAttribute('data-index'));
                    const hospital = hospitals[index];
                    map.setView([hospital.lat, hospital.lng], 15);
                    hospitalMarkers[index].openPopup();
                });
            }
        });
    }
    
    /**
     * Calculate distance between two coordinates in kilometers
     * @param {number} lat1 - Latitude of first point
     * @param {number} lon1 - Longitude of first point
     * @param {number} lat2 - Latitude of second point
     * @param {number} lon2 - Longitude of second point
     * @return {number} Distance in kilometers
     */
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Radius of the earth in km
        const dLat = deg2rad(lat2 - lat1);
        const dLon = deg2rad(lon2 - lon1);
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) * 
            Math.sin(dLon/2) * Math.sin(dLon/2); 
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
        const distance = R * c; // Distance in km
        return distance;
    }
    
    /**
     * Convert degrees to radians
     * @param {number} deg - Degrees
     * @return {number} Radians
     */
    function deg2rad(deg) {
        return deg * (Math.PI/180);
    }
});
