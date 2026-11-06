// weight_check.js — Live weight total indicator for attribute management
// Implements FR-3: Weights must sum to 100% before saving
// Implements NFR-5.1: Response within 300ms

document.addEventListener('DOMContentLoaded', function() {
    const categoryId = document.getElementById('category-id')?.value;
    const totalDisplay = document.getElementById('weight-total-value');
    const totalStatus = document.getElementById('weight-total-status');
    const weightInputs = document.querySelectorAll('.weight-input');
    
    if (!categoryId || !totalDisplay) return;
    
    // Fetch current total from server
    function fetchWeightTotal() {
        fetch(`/api/weight-total/${categoryId}`)
            .then(response => response.json())
            .then(data => {
                updateDisplay(data.total, data.is_valid, data.message);
            })
            .catch(err => console.error('Weight check failed:', err));
    }
    
    // Update the display based on total
    function updateDisplay(total, isValid, message) {
        totalDisplay.textContent = total;
        totalDisplay.className = isValid ? 'text-success' : 'text-danger';
        if (totalStatus) {
            totalStatus.textContent = message;
            totalStatus.className = isValid ? 'badge badge-success' : 'badge badge-warning';
        }
        const fill = document.getElementById('weight-progress-fill');
        if (fill) {
            const numericTotal = parseFloat(total) || 0;
            fill.style.width = Math.min(numericTotal, 100) + '%';
            if (isValid) {
                fill.className = 'progress-bar-fill bg-success';
            } else if (numericTotal > 100) {
                fill.className = 'progress-bar-fill bg-danger';
            } else {
                fill.className = 'progress-bar-fill bg-warning';
            }
        }
    }
    
    // Calculate total from form inputs (client-side for instant feedback)
    function calculateLocalTotal() {
        let total = 0;
        weightInputs.forEach(input => {
            total += parseFloat(input.value) || 0;
        });
        const isValid = Math.abs(total - 100) < 0.01;
        updateDisplay(total.toFixed(2), isValid, 
            isValid ? 'Weights sum to 100%' : `Weights sum to ${total.toFixed(2)}% (must be 100%)`);
    }
    
    // Attach listeners to weight inputs
    weightInputs.forEach(input => {
        input.addEventListener('input', calculateLocalTotal);
    });
    
    // Initial fetch from server
    fetchWeightTotal();
});
