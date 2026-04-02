/**
 * Monitor page JavaScript
 * Handles real-time status updates via polling
 */

// Configuration
const UPDATE_INTERVAL = 2000; // Poll every 2 seconds
let updateTimer = null;

/**
 * Format timestamp for display
 */
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

/**
 * Update the seat status display
 */
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update seat list
        updateSeatList(data.seats);
        
        // Update person count
        updatePersonCount(data.person_count);
        
        // Update timestamp
        updateTimestamp(data.timestamp);
        
    } catch (error) {
        console.error('Error fetching status:', error);
        showError('Failed to fetch status. Is the server running?');
    }
}

/**
 * Update the seat list UI
 */
function updateSeatList(seats) {
    const container = document.getElementById('statusContainer');
    
    if (!seats || seats.length === 0) {
        container.innerHTML = '<div class="loading">No seats configured. Please configure seats first.</div>';
        return;
    }
    
    // Build seat list HTML
    let html = '<ul class="seat-list">';
    
    seats.forEach(seat => {
        const statusClass = seat.status === 'OCCUPIED' ? 'occupied' : 'empty';
        const statusBadge = seat.status === 'OCCUPIED' ? 'status-occupied' : 'status-empty';
        
        html += `
            <li class="seat-item ${statusClass}">
                <span class="seat-label">${seat.label}</span>
                <span class="status-badge ${statusBadge}">${seat.status}</span>
            </li>
        `;
    });
    
    html += '</ul>';
    
    container.innerHTML = html;
}

/**
 * Update person count display
 */
function updatePersonCount(count) {
    const element = document.getElementById('personCount');
    element.textContent = `${count} person${count !== 1 ? 's' : ''} detected`;
}

/**
 * Update timestamp display
 */
function updateTimestamp(isoString) {
    const element = document.getElementById('lastUpdate');
    element.textContent = formatTimestamp(isoString);
}

/**
 * Show error message
 */
function showError(message) {
    const container = document.getElementById('statusContainer');
    container.innerHTML = `<div class="error">${message}</div>`;
}

/**
 * Start periodic status updates
 */
function startUpdates() {
    // Initial update
    updateStatus();
    
    // Set up periodic updates
    updateTimer = setInterval(updateStatus, UPDATE_INTERVAL);
}

/**
 * Stop periodic updates (cleanup)
 */
function stopUpdates() {
    if (updateTimer) {
        clearInterval(updateTimer);
        updateTimer = null;
    }
}

/**
 * Initialize when page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Monitor page initialized');
    startUpdates();
});

/**
 * Cleanup when page unloads
 */
window.addEventListener('beforeunload', function() {
    stopUpdates();
});

/**
 * Handle visibility change (pause updates when tab is hidden)
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopUpdates();
    } else {
        startUpdates();
    }
});
