const map = L.map('map').setView([0, 0], 2);
        let marker;
        
        L.tileLayer('https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
            attribution: '&copy; <a href="https://www.google.com/maps">Google Maps</a>',
            maxZoom: 20,
        }).addTo(map);

        function updateLocation(position) {
            const { latitude, longitude } = position.coords;
            const altitude = position.coords.altitude;
            const coords = [latitude, longitude];

            const customIcon = L.icon({
                iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', // Replace with your icon URL
                iconSize: [50, 50], // Size of the icon [width, height]
                iconAnchor: [25, 50], // Point of the icon which will correspond to marker's location [x, y]
                popupAnchor: [0, -50], // Point where the popup opens relative to the iconAnchor
              });
        
        
                    if (!marker) {
                        marker = L.marker(coords, { icon: customIcon, riseOnHover: true }).addTo(map);
                        //marker = L.marker(coords).addTo(map);
                        map.setView(coords, 15);
                    } else {
                        marker.setLatLng(coords);
                    }
                    
                    marker.bindPopup("Live Location").openPopup();
                    $('#coordinates').text(`Latitude: ${latitude.toFixed(6)}, Longitude: ${longitude.toFixed(6)}, Altitude: ${altitude}`);
                    // marker.bindPopup(L.popup({maxWidth:250,minWidth:100,maxW, autoClose:false,closeOnClick:false,className:'popup',})).setPopupcontent('Live Location').openPopup();
                    // $('#coordinates').text(`Latitude: ${latitude.toFixed(6)}, Longitude: ${longitude.toFixed(6)}, Altitude: ${altitude}`);
                      // Add Hover Effect (Dynamic Resize)
              marker.on('mouseover', function () {
                this.setIcon(
                  L.icon({
                    iconUrl: 'https://cdn-icons-png.flaticon.com/512/684/684908.png', // Same icon but larger
                    iconSize: [60, 60], // Larger size on hover
                    iconAnchor: [30, 60],
                  })
                );
              });
        
              marker.on('mouseout', function () {
                this.setIcon(customIcon); // Revert to original size
              });
                    // Send coordinates to server (if needed)
                    $.ajax({
                        url: 'your-server-endpoint',
                        method: 'POST',
                        data: { latitude, longitude },
                        success: function(response) {
                            console.log('Location updated on server');
                        },
                        error: function(xhr, status, error) {
                            console.error('Error updating location:', error);
                        }
                    });
                }
        
                function handleError(error) {
                    $('#coordinates').text(`Error: ${error.message}`);
                }
        
                if (navigator.geolocation) {
                    navigator.geolocation.watchPosition(updateLocation, handleError, {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    });
                } else {
                    $('#coordinates').text('Geolocation is not supported');
                }