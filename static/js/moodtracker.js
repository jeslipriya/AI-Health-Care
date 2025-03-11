/**
 * JavaScript for Mood Tracker functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize mood slider
    const moodSlider = document.getElementById('mood-slider');
    const moodValue = document.getElementById('mood-value');
    
    if (moodSlider && moodValue) {
        moodSlider.addEventListener('input', function() {
            updateMoodValue(this.value);
        });
        
        // Initialize with current value
        updateMoodValue(moodSlider.value);
    }
    
    // Initialize mood chart if exists
    const moodChartCanvas = document.getElementById('mood-chart');
    if (moodChartCanvas) {
        initializeMoodChart();
    }
    
    /**
     * Update the mood value display
     * @param {number} value - Mood value (1-10)
     */
    function updateMoodValue(value) {
        moodValue.textContent = value;
        
        // Update emoji and color based on mood
        const moodEmoji = document.getElementById('mood-emoji');
        const moodInput = document.getElementById('mood-slider');
        
        if (moodEmoji && moodInput) {
            let emoji, color;
            
            // Set emoji and color based on mood value
            if (value <= 2) {
                emoji = '😢';
                color = '#dc3545'; // danger red
            } else if (value <= 4) {
                emoji = '😕';
                color = '#fd7e14'; // warning orange
            } else if (value <= 6) {
                emoji = '😐';
                color = '#ffc107'; // warning yellow
            } else if (value <= 8) {
                emoji = '🙂';
                color = '#20c997'; // teal
            } else {
                emoji = '😄';
                color = '#28a745'; // success green
            }
            
            moodEmoji.textContent = emoji;
            moodInput.style.accentColor = color;
        }
    }
    
    /**
     * Initialize the mood chart
     */
    function initializeMoodChart() {
        // Get mood data from the page
        const moodData = getMoodDataFromPage();
        
        if (moodData.labels.length === 0) {
            // If no data, display message
            const chartContainer = document.getElementById('chart-container');
            chartContainer.innerHTML = '<div class="alert alert-info">No mood data recorded yet. Start tracking your mood to see a chart here.</div>';
            return;
        }
        
        // Create chart using Chart.js
        const ctx = moodChartCanvas.getContext('2d');
        const moodChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: moodData.labels,
                datasets: [{
                    label: 'Mood Score',
                    data: moodData.scores,
                    backgroundColor: 'rgba(0, 123, 255, 0.2)',
                    borderColor: 'rgba(0, 123, 255, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    pointBackgroundColor: moodData.colors,
                    pointBorderColor: '#fff',
                    pointRadius: 5,
                    pointHoverRadius: 7
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        min: 1,
                        max: 10,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Mood Score (1-10)'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            afterLabel: function(context) {
                                const index = context.dataIndex;
                                return moodData.notes[index] ? 'Notes: ' + moodData.notes[index] : '';
                            }
                        }
                    },
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    /**
     * Get mood data from the HTML
     * @return {Object} Object containing labels, scores, notes and colors arrays
     */
    function getMoodDataFromPage() {
        const moodEntries = document.querySelectorAll('.mood-entry');
        const labels = [];
        const scores = [];
        const notes = [];
        const colors = [];
        
        moodEntries.forEach(entry => {
            const date = entry.getAttribute('data-date');
            const score = parseInt(entry.getAttribute('data-score'));
            const note = entry.getAttribute('data-notes');
            
            // Format date for display
            const formattedDate = new Date(date).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            });
            
            labels.push(formattedDate);
            scores.push(score);
            notes.push(note);
            
            // Set color based on mood score
            let color;
            if (score <= 2) {
                color = '#dc3545'; // danger red
            } else if (score <= 4) {
                color = '#fd7e14'; // warning orange
            } else if (score <= 6) {
                color = '#ffc107'; // warning yellow
            } else if (score <= 8) {
                color = '#20c997'; // teal
            } else {
                color = '#28a745'; // success green
            }
            colors.push(color);
        });
        
        // Reverse arrays to show newest last
        return {
            labels: labels.reverse(),
            scores: scores.reverse(),
            notes: notes.reverse(),
            colors: colors.reverse()
        };
    }
});
