/**
 * Seat Configuration Page JavaScript
 * Handles interactive seat drawing and configuration
 */

// Canvas and drawing state
let canvas = null;
let ctx = null;
let snapshotImage = null;
let capturedImage = null;  // Store the loaded snapshot image
let isDrawing = false;
let startX = 0;
let startY = 0;
let currentRect = null;

// Seats array
let seats = [];
let nextSeatId = 1;

// Camera dimensions
let cameraWidth = 640;
let cameraHeight = 480;
let focusConfig = {
    autofocus: true,
    focus: 0,
    capabilities: {
        autofocus: false,
        focus: false
    }
};

/**
 * Initialize the page
 */
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    snapshotImage = document.getElementById('snapshotImage');
    
    // Set up mouse event listeners
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    
    // Load existing configuration
    loadExistingConfiguration();
    loadCameraSettings();

    const focusSlider = document.getElementById('focusSlider');
    const focusValue = document.getElementById('focusValue');
    const autofocusToggle = document.getElementById('autofocusToggle');

    if (focusSlider && focusValue) {
        focusSlider.addEventListener('input', () => {
            focusValue.textContent = focusSlider.value;
        });
    }

    if (autofocusToggle) {
        autofocusToggle.addEventListener('change', () => {
            updateFocusControlState();
        });
    }
    
    console.log('Configuration page initialized');
});

/**
 * Load existing seat configuration from server
 */
async function loadExistingConfiguration() {
    try {
        const response = await fetch('/api/seats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update camera dimensions
        cameraWidth = data.camera.width || 640;
        cameraHeight = data.camera.height || 480;
        
        // Load existing seats
        if (data.seats && data.seats.length > 0) {
            seats = data.seats;
            
            // Find highest seat ID to continue numbering
            const maxId = Math.max(...seats.map(s => s.id));
            nextSeatId = maxId + 1;
            
            updateSeatsList();
            showStatus('Loaded existing configuration', 'info');
        }
    } catch (error) {
        console.error('Error loading configuration:', error);
        showStatus('Could not load existing configuration', 'error');
    }
}

async function loadCameraSettings() {
    try {
        const response = await fetch('/api/camera');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        focusConfig = {
            autofocus: data.autofocus,
            focus: data.focus,
            capabilities: data.capabilities || { autofocus: false, focus: false },
            current: data.current || {}
        };

        const autofocusToggle = document.getElementById('autofocusToggle');
        const focusSlider = document.getElementById('focusSlider');
        const focusValue = document.getElementById('focusValue');

        if (autofocusToggle) {
            autofocusToggle.checked = Boolean(focusConfig.autofocus);
        }

        if (focusSlider) {
            focusSlider.value = Number(focusConfig.focus || 0);
        }

        if (focusValue) {
            focusValue.textContent = focusSlider ? focusSlider.value : '0';
        }

        updateFocusControlState();
    } catch (error) {
        console.error('Error loading camera settings:', error);
        showStatus('Could not load camera focus settings', 'error');
    }
}

function updateFocusControlState() {
    const autofocusToggle = document.getElementById('autofocusToggle');
    const focusSlider = document.getElementById('focusSlider');
    const focusNote = document.getElementById('focusNote');
    const autofocusEnabled = autofocusToggle ? autofocusToggle.checked : true;

    if (focusSlider) {
        focusSlider.disabled = autofocusEnabled || !focusConfig.capabilities.focus;
    }

    if (autofocusToggle) {
        autofocusToggle.disabled = !focusConfig.capabilities.autofocus;
    }

    if (focusNote) {
        if (!focusConfig.capabilities.autofocus && !focusConfig.capabilities.focus) {
            focusNote.textContent = 'Focus controls are not supported by this webcam.';
        } else if (autofocusEnabled) {
            focusNote.textContent = 'Autofocus is on. Disable it to adjust focus manually.';
        } else {
            focusNote.textContent = 'Manual focus enabled. Adjust the slider and apply.';
        }
    }
}

async function applyFocusSettings() {
    const autofocusToggle = document.getElementById('autofocusToggle');
    const focusSlider = document.getElementById('focusSlider');

    if (!autofocusToggle || !focusSlider) {
        return;
    }

    showStatus('Applying focus settings...', 'info');

    try {
        const response = await fetch('/api/camera/focus', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                autofocus: autofocusToggle.checked,
                focus: Number(focusSlider.value)
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            if (result.applied && (result.applied.autofocus === false || result.applied.focus === false)) {
                showStatus('Focus settings saved, but the webcam may ignore them.', 'info');
            } else {
                showStatus('Focus settings applied', 'success');
            }
            focusConfig.autofocus = autofocusToggle.checked;
            focusConfig.focus = Number(focusSlider.value);
        } else {
            showStatus('Failed to apply focus settings', 'error');
        }
    } catch (error) {
        console.error('Error applying focus settings:', error);
        showStatus('Failed to apply focus settings', 'error');
    }
}

function resetFocusSettings() {
    const autofocusToggle = document.getElementById('autofocusToggle');
    const focusSlider = document.getElementById('focusSlider');
    const focusValue = document.getElementById('focusValue');

    if (!autofocusToggle || !focusSlider) {
        return;
    }

    autofocusToggle.checked = Boolean(focusConfig.autofocus);
    focusSlider.value = Number(focusConfig.focus || 0);
    if (focusValue) {
        focusValue.textContent = focusSlider.value;
    }
    updateFocusControlState();
    showStatus('Focus settings reset', 'info');
}

/**
 * Capture a frame from the camera
 */
async function captureFrame() {
    showStatus('Capturing frame...', 'info');
    
    try {
        const response = await fetch('/api/snapshot');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        
        // Load image
        const img = new Image();
        img.onload = function() {
            // Store the image for later redraws
            capturedImage = img;
            
            // Set canvas size to match image
            canvas.width = img.width;
            canvas.height = img.height;
            
            // Draw image on canvas
            ctx.drawImage(img, 0, 0);
            
            // Redraw existing seats
            redrawSeats();
            
            showStatus('Frame captured! Draw rectangles to define seats.', 'success');
        };
        img.onerror = function() {
            showStatus('Failed to load snapshot image', 'error');
        };
        img.src = imageUrl;
        
    } catch (error) {
        console.error('Error capturing frame:', error);
        showStatus('Failed to capture frame. Is the camera working?', 'error');
    }
}

/**
 * Handle mouse down event (start drawing)
 */
function handleMouseDown(e) {
    if (canvas.width === 0 || canvas.height === 0) {
        showStatus('Please capture a frame first!', 'error');
        return;
    }
    
    isDrawing = true;
    const rect = canvas.getBoundingClientRect();
    startX = Math.round((e.clientX - rect.left) * (canvas.width / rect.width));
    startY = Math.round((e.clientY - rect.top) * (canvas.height / rect.height));
}

/**
 * Handle mouse move event (draw preview)
 */
function handleMouseMove(e) {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const currentX = Math.round((e.clientX - rect.left) * (canvas.width / rect.width));
    const currentY = Math.round((e.clientY - rect.top) * (canvas.height / rect.height));
    
    // Redraw everything
    redrawCanvas();
    
    // Draw preview rectangle
    ctx.strokeStyle = '#ffff00';
    ctx.lineWidth = 3;
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(startX, startY, currentX - startX, currentY - startY);
    ctx.setLineDash([]);
}

/**
 * Handle mouse up event (finish drawing)
 */
function handleMouseUp(e) {
    if (!isDrawing) return;
    
    isDrawing = false;
    
    const rect = canvas.getBoundingClientRect();
    const endX = Math.round((e.clientX - rect.left) * (canvas.width / rect.width));
    const endY = Math.round((e.clientY - rect.top) * (canvas.height / rect.height));
    
    // Normalize coordinates (ensure x1 < x2, y1 < y2)
    const x1 = Math.min(startX, endX);
    const y1 = Math.min(startY, endY);
    const x2 = Math.max(startX, endX);
    const y2 = Math.max(startY, endY);
    
    // Validate minimum size
    const minSize = 20;
    if (x2 - x1 < minSize || y2 - y1 < minSize) {
        showStatus('Rectangle too small. Please draw a larger area.', 'error');
        redrawCanvas();
        return;
    }
    
    // Add new seat
    const newSeat = {
        id: nextSeatId++,
        label: `Seat ${seats.length + 1}`,
        x1: x1,
        y1: y1,
        x2: x2,
        y2: y2
    };
    
    seats.push(newSeat);
    
    // Update UI
    redrawCanvas();
    updateSeatsList();
    showStatus(`Added ${newSeat.label}`, 'success');
}

/**
 * Redraw the entire canvas
 */
function redrawCanvas() {
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Redraw snapshot (if exists)
    if (capturedImage) {
        ctx.drawImage(capturedImage, 0, 0);
    }
    
    // Redraw seats
    redrawSeats();
}

/**
 * Redraw all seats on canvas
 */
function redrawSeats() {
    seats.forEach((seat, index) => {
        // Alternate colors for visibility
        const colors = ['#00ff00', '#00ffff', '#ff00ff', '#ff8800'];
        const color = colors[index % colors.length];
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(seat.x1, seat.y1, seat.x2 - seat.x1, seat.y2 - seat.y1);
        
        // Draw label
        ctx.fillStyle = color;
        ctx.font = 'bold 16px Arial';
        ctx.fillText(seat.label, seat.x1 + 5, seat.y1 - 5);
    });
}

/**
 * Update the seats list UI
 */
function updateSeatsList() {
    const container = document.getElementById('seatsList');
    const countElement = document.getElementById('seatCount');
    
    countElement.textContent = seats.length;
    
    if (seats.length === 0) {
        container.innerHTML = `
            <div class="empty-seats">
                No seats configured yet.<br>
                Draw rectangles on the canvas to add seats.
            </div>
        `;
        return;
    }
    
    let html = '';
    
    seats.forEach((seat, index) => {
        html += `
            <div class="seat-config-item">
                <div class="seat-config-header">
                    <span class="seat-config-label">Seat ${index + 1}</span>
                    <button class="btn-delete" onclick="deleteSeat(${seat.id})">Delete</button>
                </div>
                <div class="seat-config-coords">
                    Position: (${seat.x1}, ${seat.y1}) to (${seat.x2}, ${seat.y2})
                </div>
                <input 
                    type="text" 
                    class="seat-config-input" 
                    value="${seat.label}"
                    onchange="updateSeatLabel(${seat.id}, this.value)"
                    placeholder="Enter seat label"
                >
            </div>
        `;
    });
    
    container.innerHTML = html;
}

/**
 * Update seat label
 */
function updateSeatLabel(seatId, newLabel) {
    const seat = seats.find(s => s.id === seatId);
    if (seat) {
        seat.label = newLabel || `Seat ${seatId}`;
        redrawCanvas();
        showStatus('Label updated', 'success');
    }
}

/**
 * Delete a seat
 */
function deleteSeat(seatId) {
    seats = seats.filter(s => s.id !== seatId);
    updateSeatsList();
    redrawCanvas();
    showStatus('Seat deleted', 'info');
}

/**
 * Clear all seats
 */
function clearCanvas() {
    if (seats.length === 0) {
        showStatus('No seats to clear', 'info');
        return;
    }
    
    if (confirm('Are you sure you want to clear all seats?')) {
        seats = [];
        nextSeatId = 1;
        updateSeatsList();
        redrawCanvas();
        showStatus('All seats cleared', 'info');
    }
}

/**
 * Undo last seat
 */
function undoLastSeat() {
    if (seats.length === 0) {
        showStatus('No seats to undo', 'info');
        return;
    }
    
    const removed = seats.pop();
    updateSeatsList();
    redrawCanvas();
    showStatus(`Removed ${removed.label}`, 'info');
}

/**
 * Save configuration to server
 */
async function saveConfiguration() {
    if (seats.length === 0) {
        showStatus('Please add at least one seat before saving', 'error');
        return;
    }
    
    showStatus('Saving configuration...', 'info');
    
    try {
        const response = await fetch('/api/seats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ seats: seats })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            showStatus(`Configuration saved! ${result.message}`, 'success');
            
            // Redirect to main page after 2 seconds
            setTimeout(() => {
                window.location.href = '/';
            }, 2000);
        } else {
            showStatus('Failed to save: ' + (result.error || 'Unknown error'), 'error');
        }
        
    } catch (error) {
        console.error('Error saving configuration:', error);
        showStatus('Failed to save configuration. Please try again.', 'error');
    }
}

/**
 * Show status message
 */
function showStatus(message, type) {
    const container = document.getElementById('statusMessage');
    container.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
    
    // Auto-hide success/info messages after 5 seconds
    if (type === 'success' || type === 'info') {
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    }
}
