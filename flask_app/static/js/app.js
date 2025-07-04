/**
 * Beautiful Flicker - Frontend Application
 */

// Application state
const appState = {
    sessionId: null,
    currentData: null,
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
        legend_items: []
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
    closeError: document.getElementById('closeError')
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
    
    // Chart type selector
    document.querySelectorAll('.chart-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            appState.currentChartType = e.target.dataset.chartType;
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
            if (data.success && data.examples) {
                // Examples are hardcoded in HTML for now
                // Could dynamically populate from API if needed
            }
        })
        .catch(error => console.error('Failed to load examples:', error));
}

function handleExampleSelect(event) {
    const example = event.target.value;
    if (!example) return;
    
    // Map dropdown values to actual filenames
    const exampleMap = {
        '60hz_incandescent': '60hz_incandescent.csv',
        'led_pwm': 'led_pwm_dimming.csv',
        'fluorescent_magnetic': 'fluorescent_magnetic.csv',
        'sample_flicker': 'Example_Waveform.csv'
    };
    
    const filename = exampleMap[example] || example;
    
    showLoading();
    
    fetch(`/api/example/${filename}`)
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
    if (!appState.sessionId) return;
    
    showLoading();
    
    fetch(`/api/chart/${appState.currentChartType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: appState.sessionId,
            config: appState.chartSettings
        })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            displayChart(data.chart);
        } else {
            showError(data.error || 'Failed to generate chart');
        }
    })
    .catch(error => {
        hideLoading();
        showError('Network error: ' + error.message);
    });
}

function displayChart(chartData) {
    elements.chartDisplay.innerHTML = `<img src="${chartData.image}" alt="Flicker ${chartData.type} chart">`;
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