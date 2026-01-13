function updateMapViz() {
    const mapBubblesContainer = document.getElementById('mapBubbles');
    if (mapBubblesContainer && realData) {
        mapBubblesContainer.innerHTML = '';

        // Responsive Percentages (Top/Left) based on the specific map image aspect ratio
        // Estimation for standard vertical Israel map:
        const cityPositions = {
            'jerusalem': { top: 48, left: 50, color: '#f59e0b' },  // ~Center
            'telaviv': { top: 42, left: 35, color: '#ef4444' },  // ~Coast Center
            'haifa': { top: 25, left: 40, color: '#3b82f6' },  // ~North Coast
            'beersheva': { top: 65, left: 45, color: '#f97316' },  // ~South
            'petah_tikva': { top: 41, left: 40, color: '#10b981' } // ~Near TLV
        };

        const cityKeys = Object.keys(cityPositions);

        cityKeys.forEach(key => {
            if (realData[key] && realData[key]['all']) {
                const total = realData[key]['all'].total;
                const pos = cityPositions[key];

                // Dynamic Size
                const size = Math.max(30, Math.sqrt(total) * 4); // px size

                const bubble = document.createElement('div');
                bubble.className = "map-bubble";
                bubble.style.width = `${size}px`;
                bubble.style.height = `${size}px`;
                bubble.style.backgroundColor = pos.color;
                bubble.style.left = `${pos.left}%`;
                bubble.style.top = `${pos.top}%`;

                // Tooltip logic
                bubble.innerHTML = `
                            <span class="count">${total}</span>
                            <div class="tooltip">
                                <strong>${key === 'jerusalem' ? 'ירושלים' :
                        key === 'telaviv' ? 'תל אביב' :
                            key === 'haifa' ? 'חיפה' :
                                key === 'beersheva' ? 'באר שבע' : 'פתח תקווה'}</strong><br>
                                ${total} מעצרים
                            </div>
                        `;

                mapBubblesContainer.appendChild(bubble);
            }
        });
    }
}
