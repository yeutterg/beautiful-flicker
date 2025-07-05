/**
 * Beautiful Flicker - Frontend Application
 */

// Application state
const appState = {
    sessionId: null,
    currentData: null,
    selectedDatasets: new Map(), // For multiple dataset selection
    manualPoints: [], // For manual entry points
    chartSettings: {
        title: '',
        font: 'Inter',
        title_size: 24,
        axis_label_size: 14,
        legend_size: 12,
        show_metrics: true,
        show_standards: true,
        show_legend: false,
        legend_position: 'top right',
        format: 'png',
        export_dpi: 300
    },
    exportSettings: {
        format: 'png',
        transparent_bg: false,
        export_dpi: 300,
        size_preset: 'auto'
    },
    currentChartType: 'waveform'
};

// DOM Elements
const elements = {
    // File upload
    dropZone: document.getElementById('dropZone'),
    fileInput: document.getElementById('fileInput'),
    csvPaste: document.getElementById('csvPaste'),
    processPastedData: document.getElementById('processPastedData'),
    exampleSelect: document.getElementById('exampleSelect'),
    
    // Data preview
    dataPreview: document.getElementById('dataPreview'),
    totalRows: document.getElementById('totalRows'),
    duration: document.getElementById('duration'),
    sampleRate: document.getElementById('sampleRate'),
    previewTableBody: document.getElementById('previewTableBody'),
    
    // Chart configuration
    chartConfigSection: document.getElementById('chartConfigSection'),
    chartTitle: document.getElementById('chartTitle'),
    fontSelect: document.getElementById('fontSelect'),
    titleSize: document.getElementById('titleSize'),
    axisLabelSize: document.getElementById('axisLabelSize'),
    legendSize: document.getElementById('legendSize'),
    showMetrics: document.getElementById('showMetrics'),
    showStandards: document.getElementById('showStandards'),
    showLegend: document.getElementById('showLegend'),
    legendConfig: document.getElementById('legendConfig'),
    
    // Visualization
    visualizationSection: document.getElementById('visualizationSection'),
    chartDisplay: document.getElementById('chartDisplay'),
    analysisResults: document.getElementById('analysisResults'),
    
    // Export
    exportSection: document.getElementById('exportSection'),
    exportChart: document.getElementById('exportChart'),
    transparentBg: document.getElementById('transparentBg'),
    sizePreset: document.getElementById('sizePreset'),
    customSize: document.getElementById('customSize'),
    
    // Loading and error
    loadingOverlay: document.getElementById('loadingOverlay'),
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage'),
    closeError: document.getElementById('closeError'),
    
    // Manual entry
    manualFrequency: document.getElementById('manual-frequency'),
    manualModulation: document.getElementById('manual-modulation'),
    manualLabel: document.getElementById('manual-label'),
    addManualPoint: document.getElementById('add-manual-point'),
    manualPointsList: document.getElementById('manual-points-list'),
    manualPointsContainer: document.getElementById('manual-points-container')
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadExamples();
});

// Event Listeners Setup
function setupEventListeners() {
    // File upload
    elements.dropZone.addEventListener('click', () => elements.fileInput.click());
    elements.fileInput.addEventListener('change', handleFileSelect);
    elements.dropZone.addEventListener('dragover', handleDragOver);
    elements.dropZone.addEventListener('dragleave', handleDragLeave);
    elements.dropZone.addEventListener('drop', handleDrop);
    
    // Paste CSV
    elements.processPastedData.addEventListener('click', handlePastedData);
    
    // Example selection
    elements.exampleSelect.addEventListener('change', handleExampleSelect);
    
    // Chart configuration
    elements.chartTitle.addEventListener('input', updateChartConfig);
    elements.fontSelect.addEventListener('change', updateChartConfig);
    elements.showMetrics.addEventListener('change', updateChartConfig);
    elements.showStandards.addEventListener('change', updateChartConfig);
    elements.showLegend.addEventListener('change', () => {
        updateChartConfig();
        elements.legendConfig.style.display = elements.showLegend.checked ? 'block' : 'none';
    });
    
    // Size sliders
    setupSlider('titleSize');
    setupSlider('axisLabelSize');
    setupSlider('legendSize');
    
    // Legend position
    document.querySelectorAll('.position-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.position-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            appState.chartSettings.legend_position = e.target.dataset.position;
            updateChart();
        });
    });
    
    // Chart type switching
    document.querySelectorAll('.chart-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active class from all buttons
            document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            e.target.classList.add('active');
            
            // Update current chart type
            appState.currentChartType = e.target.dataset.chartType;
            
            // Show visualization section if not already visible
            elements.visualizationSection.style.display = 'block';
            
            // Update chart
            updateChart();
        });
    });
    
    // Export format
    document.querySelectorAll('.format-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            appState.exportSettings.format = e.target.dataset.format;
        });
    });
    
    // Export settings
    elements.transparentBg.addEventListener('change', () => {
        appState.exportSettings.transparent_bg = elements.transparentBg.checked;
    });
    
    elements.sizePreset.addEventListener('change', () => {
        appState.exportSettings.size_preset = elements.sizePreset.value;
        elements.customSize.style.display = elements.sizePreset.value === 'custom' ? 'block' : 'none';
    });
    
    // Resolution radio buttons
    document.querySelectorAll('input[name="resolution"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'custom') {
                appState.exportSettings.export_dpi = parseInt(document.getElementById('customDPI').value);
            } else {
                appState.exportSettings.export_dpi = parseInt(e.target.value);
            }
        });
    });
    
    document.getElementById('customDPI').addEventListener('input', (e) => {
        if (document.querySelector('input[name="resolution"]:checked').value === 'custom') {
            appState.exportSettings.export_dpi = parseInt(e.target.value);
        }
    });
    
    // Export button
    elements.exportChart.addEventListener('click', handleExport);
    
    // Error modal
    elements.closeError.addEventListener('click', () => {
        elements.errorModal.style.display = 'none';
    });
    
    // Manual entry
    elements.addManualPoint.addEventListener('click', handleAddManualPoint);
    
    // Chart controls
    document.getElementById('resetZoom').addEventListener('click', () => {
        updateChart();
    });
    
    document.getElementById('fullscreen').addEventListener('click', () => {
        if (elements.chartDisplay.requestFullscreen) {
            elements.chartDisplay.requestFullscreen();
        }
    });
}

// File Handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.dropZone.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.dropZone.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.dropZone.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

function processFile(file) {
    if (file.size > 50 * 1024 * 1024) {
        showError('File size exceeds 50MB limit');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            handleUploadSuccess(data);
        } else {
            showError(data.error || 'Failed to process file');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Network error: ' + error.message);
    });
}

// Pasted Data Handling
function handlePastedData() {
    const csvData = elements.csvPaste.value.trim();
    if (!csvData) {
        showError('Please paste CSV data first');
        return;
    }
    
    showLoading();
    
    fetch('/api/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ csv_data: csvData })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            handleUploadSuccess(data);
        } else {
            showError(data.error || 'Failed to process data');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Network error: ' + error.message);
    });
}

// Example Handling
function loadExamples() {
    fetch('/api/examples')
        .then(response => response.json())
        .then(data => {
            if (data.success && Array.isArray(data.examples)) {
                // Clear existing options
                elements.exampleSelect.innerHTML = '<option value="">Select an example...</option>';
                // Populate dropdown
                data.examples.forEach(ex => {
                    const option = document.createElement('option');
                    option.value = encodeURIComponent(ex.path); // keep slashes but URI-encode
                    option.textContent = ex.name;
                    elements.exampleSelect.appendChild(option);
                });
            }
        })
        .catch(error => console.error('Failed to load examples:', error));
}

function handleExampleSelect(event) {
    const encodedPath = event.target.value;
    if (!encodedPath) return;

    showLoading();
    fetch(`/api/example/${encodedPath}`)
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                handleUploadSuccess(data);
            } else {
                showError(data.error || 'Failed to load example');
            }
        })
        .catch(error => {
            hideLoading();
            showError('Network error: ' + error.message);
        });
}

// Upload Success Handler
function handleUploadSuccess(data) {
    appState.sessionId = data.session_id;
    appState.currentData = data;
    
    // Show data preview
    displayDataPreview(data.preview);
    
    // Display analysis results
    displayAnalysisResults(data.analysis);
    
    // Show configuration and visualization sections
    elements.chartConfigSection.style.display = 'block';
    elements.visualizationSection.style.display = 'block';
    elements.exportSection.style.display = 'block';
    
    // Generate initial chart
    updateChart();
    
    // Scroll to preview
    elements.dataPreview.scrollIntoView({ behavior: 'smooth' });
}

// Data Preview Display
function displayDataPreview(preview) {
    elements.dataPreview.style.display = 'block';
    
    // Update stats
    elements.totalRows.textContent = preview.total_rows;
    elements.duration.textContent = preview.time_range.duration.toFixed(3);
    
    // Calculate sample rate
    const sampleRate = Math.round(preview.total_rows / preview.time_range.duration);
    elements.sampleRate.textContent = sampleRate;
    
    // Clear and populate preview table
    elements.previewTableBody.innerHTML = '';
    preview.data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.time.toFixed(6)}</td>
            <td>${row.value.toFixed(6)}</td>
        `;
        elements.previewTableBody.appendChild(tr);
    });
}

// Analysis Results Display
function displayAnalysisResults(analysis) {
    // Flicker metrics
    document.getElementById('resultFrequency').textContent = `${analysis.frequency} Hz`;
    document.getElementById('resultPercent').textContent = `${analysis.percent_flicker}%`;
    document.getElementById('resultIndex').textContent = analysis.flicker_index;
    document.getElementById('resultRMS').textContent = analysis.rms_variation ? 
        `${analysis.rms_variation}%` : '--';
    
    // Standards compliance
    updateStandardsResult('resultIEEE', analysis.ieee_1789_2015);
    updateStandardsResult('resultJA8', analysis.california_ja8_2019 ? 'Pass' : 'Fail');
    updateStandardsResult('resultWELL', analysis.well_standard_v2 ? 'Pass' : 'Fail');
}

function updateStandardsResult(elementId, result) {
    const element = document.getElementById(elementId);
    element.textContent = result;
    
    // Remove all status classes
    element.removeAttribute('data-status');
    
    // Add appropriate status class
    if (result === 'Pass' || result === 'No Risk') {
        element.setAttribute('data-status', result === 'Pass' ? 'pass' : 'no-risk');
    } else if (result === 'Low Risk') {
        element.setAttribute('data-status', 'low-risk');
    } else if (result === 'Fail' || result === 'High Risk') {
        element.setAttribute('data-status', result === 'Fail' ? 'fail' : 'high-risk');
    }
}

// Chart Configuration
function updateChartConfig() {
    appState.chartSettings.title = elements.chartTitle.value;
    appState.chartSettings.font = elements.fontSelect.value;
    appState.chartSettings.show_metrics = elements.showMetrics.checked;
    appState.chartSettings.show_standards = elements.showStandards.checked;
    appState.chartSettings.show_legend = elements.showLegend.checked;
    
    updateChart();
}

function setupSlider(sliderId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = slider.nextElementSibling;
    
    slider.addEventListener('input', (e) => {
        const value = e.target.value;
        valueDisplay.textContent = `${value}px`;
        
        // Update app state
        const settingKey = sliderId.replace(/([A-Z])/g, '_$1').toLowerCase();
        appState.chartSettings[settingKey] = parseInt(value);
        
        updateChart();
    });
}

// Chart Generation
function updateChart() {
    // If IEEE chart and we have manual points but no session, use manual-only endpoint
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0 && !appState.sessionId) {
        generateManualOnlyIEEEChart();
        return;
    }
    
    // If IEEE chart with no manual points and no session, show message
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length === 0 && !appState.sessionId) {
        elements.chartDisplay.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>Add manual points above to view IEEE 1789-2015 compliance chart</p></div>';
        return;
    }
    
    // If not IEEE chart and no session, show message to load data
    if (!appState.sessionId) {
        elements.chartDisplay.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>Please load data or select an example to view charts</p></div>';
        return;
    }
    
    showLoading();
    
    // Prepare config with manual points for IEEE charts
    const config = { ...appState.chartSettings };
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0) {
        config.manual_points = appState.manualPoints;
    }
    
    fetch(`/api/chart/${appState.currentChartType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: appState.sessionId,
            config: config
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.chart && data.chart.image) {
                elements.chartDisplay.innerHTML = `<img src="${data.chart.image}" alt="Chart" style="max-width: 100%; height: auto;">`;
            }
        } else {
            showError(data.error || 'Failed to generate chart');
        }
    })
    .catch(error => {
        console.error('Chart generation error:', error);
        showError('Failed to generate chart');
    })
    .finally(() => {
        hideLoading();
    });
}

function generateManualOnlyIEEEChart() {
    if (appState.manualPoints.length === 0) {
        elements.chartDisplay.innerHTML = '<p>Add manual points to view IEEE chart</p>';
        return;
    }
    
    showLoading();
    
    const config = { 
        ...appState.chartSettings,
        manual_points: appState.manualPoints 
    };
    
    fetch('/api/chart/ieee/manual', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            config: config
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.chart && data.chart.image) {
                elements.chartDisplay.innerHTML = `<img src="${data.chart.image}" alt="IEEE Chart with Manual Points" style="max-width: 100%; height: auto;">`;
            }
        } else {
            showError(data.error || 'Failed to generate manual IEEE chart');
        }
    })
    .catch(error => {
        console.error('Manual IEEE chart generation error:', error);
        showError('Failed to generate manual IEEE chart');
    })
    .finally(() => {
        hideLoading();
    });
}

// Export Handling
function handleExport() {
    if (!appState.sessionId) return;
    
    // Prepare export configuration
    const exportConfig = { ...appState.exportSettings };
    
    if (exportConfig.size_preset === 'letter') {
        exportConfig.fig_width = 8.5;
        exportConfig.fig_height = 11;
    } else if (exportConfig.size_preset === 'a4') {
        exportConfig.fig_width = 8.27;  // 210mm in inches
        exportConfig.fig_height = 11.69; // 297mm in inches
    } else if (exportConfig.size_preset === 'custom') {
        const widthUnit = document.getElementById('widthUnit').value;
        const heightUnit = document.getElementById('heightUnit').value;
        let width = parseFloat(document.getElementById('customWidth').value);
        let height = parseFloat(document.getElementById('customHeight').value);
        
        // Convert to inches if needed
        if (widthUnit === 'cm') width = width / 2.54;
        if (heightUnit === 'cm') height = height / 2.54;
        
        exportConfig.fig_width = width;
        exportConfig.fig_height = height;
    }
    
    showLoading();
    
    fetch(`/api/export/${appState.exportSettings.format}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: appState.sessionId,
            chart_type: appState.currentChartType,
            export_config: exportConfig
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        } else {
            throw new Error('Export failed');
        }
    })
    .then(blob => {
        hideLoading();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `flicker_${appState.currentChartType}.${appState.exportSettings.format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        hideLoading();
        showError('Export failed: ' + error.message);
    });
}

// UI Helpers
function showLoading() {
    elements.loadingOverlay.style.display = 'flex';
}

function hideLoading() {
    elements.loadingOverlay.style.display = 'none';
}

function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorModal.style.display = 'flex';
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Debounced chart update
const debouncedChartUpdate = debounce(updateChart, 500);

// Manual Point Management
function handleAddManualPoint() {
    const frequency = parseFloat(elements.manualFrequency.value);
    const modulation = parseFloat(elements.manualModulation.value);
    const label = elements.manualLabel.value.trim() || `Point ${appState.manualPoints.length + 1}`;
    
    if (!frequency || !modulation) {
        showError('Please enter both frequency and modulation values');
        return;
    }
    
    if (frequency < 1 || frequency > 10000) {
        showError('Frequency must be between 1 and 10000 Hz');
        return;
    }
    
    if (modulation < 0.01 || modulation > 100) {
        showError('Modulation must be between 0.01 and 100%');
        return;
    }
    
    // Add to manual points
    const point = {
        id: Date.now(),
        frequency: frequency,
        modulation: modulation,
        label: label
    };
    
    appState.manualPoints.push(point);
    
    // Clear inputs
    elements.manualFrequency.value = '';
    elements.manualModulation.value = '';
    elements.manualLabel.value = '';
    
    // Update display
    updateManualPointsDisplay();
    
    // If this is the first manual point and no session data, automatically switch to IEEE chart
    if (appState.manualPoints.length === 1 && !appState.sessionId) {
        // Show visualization section
        elements.visualizationSection.style.display = 'block';
        
        // Switch to IEEE chart
        document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
        const ieeeBtn = document.querySelector('.chart-type-btn[data-chart-type="ieee"]');
        if (ieeeBtn) {
            ieeeBtn.classList.add('active');
            appState.currentChartType = 'ieee';
        }
    }
    
    // If IEEE chart is currently active, update it (works with or without session data)
    if (appState.currentChartType === 'ieee') {
        updateChart();
    }
    
    console.log(`Added manual point: ${label} (${frequency} Hz, ${modulation}%)`);
}

function updateManualPointsDisplay() {
    if (appState.manualPoints.length === 0) {
        elements.manualPointsList.style.display = 'none';
        return;
    }
    
    elements.manualPointsList.style.display = 'block';
    elements.manualPointsContainer.innerHTML = '';
    
    appState.manualPoints.forEach(point => {
        const item = document.createElement('div');
        item.className = 'manual-point-item';
        item.innerHTML = `
            <div class="manual-point-info">
                <strong>${point.label}</strong>: ${point.frequency} Hz, ${point.modulation}%
            </div>
            <button class="manual-point-remove" onclick="removeManualPoint(${point.id})">×</button>
        `;
        elements.manualPointsContainer.appendChild(item);
    });
}

function removeManualPoint(pointId) {
    appState.manualPoints = appState.manualPoints.filter(p => p.id !== pointId);
    updateManualPointsDisplay();
    
    // If IEEE chart is currently active, update it (works with or without session data)
    if (appState.currentChartType === 'ieee') {
        updateChart();
    }
    
    console.log('Manual point removed');
}