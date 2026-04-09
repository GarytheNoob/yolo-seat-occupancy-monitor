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
        
        // Update counts display
        updateCounts(data.summary);
        
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
        // Determine status class and badge class based on tri-state status
        let statusClass = 'empty';
        let statusBadge = 'status-empty';
        
        if (seat.status === 'OCCUPIED') {
            statusClass = 'occupied';
            statusBadge = 'status-occupied';
        } else if (seat.status === 'RESERVED') {
            statusClass = 'reserved';
            statusBadge = 'status-reserved';
        }
        
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
 * Update counts display (people, items, and seat summary)
 */
function updateCounts(summary) {
    const personCountElement = document.getElementById('personCount');
    const itemCountElement = document.getElementById('itemCount');
    
    if (summary) {
        // Update person count
        const personCount = summary.total_people || 0;
        personCountElement.textContent = `${personCount} person${personCount !== 1 ? 's' : ''} detected`;
        
        // Update item count
        const itemCount = summary.total_items || 0;
        if (itemCount > 0) {
            itemCountElement.textContent = ` | ${itemCount} item${itemCount !== 1 ? 's' : ''} detected`;
            itemCountElement.style.display = 'inline';
        } else {
            itemCountElement.style.display = 'none';
        }
    } else {
        personCountElement.textContent = 'Detecting...';
        itemCountElement.style.display = 'none';
    }
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
