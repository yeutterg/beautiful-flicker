/**
 * Beautiful Flicker - Frontend Application
 */

// Application state
const appState = {
    sessionId: null,
    currentData: null,
    selectedDatasets: new Map(), // For multiple dataset selection
    activeDatasets: [], // Array of active datasets for display
    manualPoints: [], // For manual entry points
    dataLabel: 'Data', // Label for current dataset
    chartSettings: {
        title: '',
        font: 'Inter',
        title_size: 16,
        axis_label_size: 12,
        legend_size: 10,
        show_metrics: true,
        show_standards: true,
        show_legend: true,
        legend_position: 'upper left',
        format: 'png',
        export_dpi: 300,
        width: 10,
        height: 6,
        width_px: 1200,
        height_px: 800,
        resolution_type: 'dpi',
        aspect_ratio_locked: true
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
    // Data input
    uploadArea: document.getElementById('upload-area'),
    fileInput: document.getElementById('file-input'),
    uploadLabel: document.getElementById('upload-label'),
    csvPaste: document.getElementById('csv-paste'),
    pasteLabel: document.getElementById('paste-label'),
    processPaste: document.getElementById('process-paste'),
    exampleSelect: document.getElementById('example-select'),
    exampleLabel: document.getElementById('example-label'),
    
    // Input tabs
    inputTabs: document.querySelectorAll('.input-tab'),
    inputContents: document.querySelectorAll('.input-content'),
    
    // Chart configuration
    chartTitle: document.getElementById('chart-title'),
    fontFamily: document.getElementById('font-family'),
    titleFontSize: document.getElementById('title-font-size'),
    axisFontSize: document.getElementById('axis-font-size'),
    legendFontSize: document.getElementById('legend-font-size'),
    showMetrics: document.getElementById('show-metrics'),
    showStandards: document.getElementById('show-standards'),
    showLegend: document.getElementById('show-legend'),
    legendPosition: document.getElementById('legend-position'),
    
    // Export configuration
    chartFormat: document.getElementById('chart-format'),
    resolutionType: document.getElementById('resolution-type'),
    chartDpi: document.getElementById('chart-dpi'),
    customDpi: document.getElementById('custom-dpi'),
    customDpiGroup: document.getElementById('custom-dpi-group'),
    dpiSettings: document.getElementById('dpi-settings'),
    pixelSettings: document.getElementById('pixel-settings'),
    chartWidth: document.getElementById('chart-width'),
    chartHeight: document.getElementById('chart-height'),
    chartWidthPx: document.getElementById('chart-width-px'),
    chartHeightPx: document.getElementById('chart-height-px'),
    aspectRatioLock: document.getElementById('aspect-ratio-lock'),
    
    // Visualization
    visualizationSection: document.getElementById('visualizationSection'),
    chartConfigSection: document.getElementById('chartConfigSection'),
    exportSection: document.getElementById('exportSection'),
    chartDisplay: document.getElementById('chartDisplay'),
    loadingSpinner: document.getElementById('loadingOverlay'),
    analysisResults: document.getElementById('analysisResults'),
    
    // Data preview
    dataPreview: document.getElementById('dataPreview'),
    totalRows: document.getElementById('totalRows'),
    duration: document.getElementById('duration'),
    sampleRate: document.getElementById('sampleRate'),
    previewTableBody: document.getElementById('previewTableBody'),
    
    // Manual entry
    manualFrequency: document.getElementById('manual-frequency'),
    manualModulation: document.getElementById('manual-modulation'),
    manualLabel: document.getElementById('manual-label'),
    addManualPoint: document.getElementById('add-manual-point'),
    manualPointsList: document.getElementById('manual-points-list'),
    manualPointsContainer: document.getElementById('manual-points-container'),
    
    // Error modal
    errorModal: document.getElementById('errorModal'),
    errorMessage: document.getElementById('errorMessage'),
    closeError: document.getElementById('closeError'),
    
    // Active datasets
    activeDatasetsSection: document.getElementById('activeDatasetsSection'),
    datasetsList: document.getElementById('datasetsList'),
    clearAllDatasets: document.getElementById('clearAllDatasets')
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadExamples();
});

// Dataset Management Functions
function addDataset(sessionId, label, analysis) {
    // Add to active datasets
    appState.activeDatasets.push({
        sessionId: sessionId,
        label: label,
        analysis: analysis
    });
    
    // Update UI
    updateDatasetsList();
    
    // Show datasets section if multiple datasets
    if (appState.activeDatasets.length > 0) {
        elements.activeDatasetsSection.style.display = 'block';
    }
}

function removeDataset(index) {
    appState.activeDatasets.splice(index, 1);
    updateDatasetsList();
    
    // Hide section if no datasets
    if (appState.activeDatasets.length === 0) {
        elements.activeDatasetsSection.style.display = 'none';
    }
    
    // Update chart
    updateChart();
}

function clearAllDatasets() {
    appState.activeDatasets = [];
    updateDatasetsList();
    elements.activeDatasetsSection.style.display = 'none';
    updateChart();
}

function updateDatasetsList() {
    elements.datasetsList.innerHTML = '';
    
    if (appState.activeDatasets.length === 0) {
        elements.datasetsList.innerHTML = '<p style="text-align: center; color: #666;">No datasets loaded</p>';
        return;
    }
    
    appState.activeDatasets.forEach((dataset, index) => {
        const item = document.createElement('div');
        item.className = 'dataset-item';
        item.innerHTML = `
            <span class="dataset-name">${dataset.label}</span>
            <button class="btn btn-small" onclick="removeDataset(${index})">Remove</button>
        `;
        elements.datasetsList.appendChild(item);
    });
}

// Event Listeners Setup
function setupEventListeners() {
    // Input tabs
    elements.inputTabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
            const tabName = e.target.dataset.tab;
            switchInputTab(tabName);
        });
    });
    
    // File upload
    elements.uploadArea.addEventListener('click', () => elements.fileInput.click());
    elements.uploadArea.addEventListener('dragover', handleDragOver);
    elements.uploadArea.addEventListener('dragleave', handleDragLeave);
    elements.uploadArea.addEventListener('drop', handleDrop);
    elements.fileInput.addEventListener('change', handleFileSelect);
    
    // CSV paste
    elements.processPaste.addEventListener('click', handlePasteData);
    
    // Example selection
    elements.exampleSelect.addEventListener('change', handleExampleSelect);
    
    // Chart configuration
    elements.chartTitle.addEventListener('input', updateChartSettings);
    elements.fontFamily.addEventListener('change', updateChartSettings);
    elements.titleFontSize.addEventListener('input', updateChartSettings);
    elements.axisFontSize.addEventListener('input', updateChartSettings);
    elements.legendFontSize.addEventListener('input', updateChartSettings);
    elements.showMetrics.addEventListener('change', updateChartSettings);
    elements.showStandards.addEventListener('change', updateChartSettings);
    elements.showLegend.addEventListener('change', updateChartSettings);
    elements.legendPosition.addEventListener('change', updateChartSettings);
    
    // Export configuration
    elements.resolutionType.addEventListener('change', handleResolutionTypeChange);
    elements.chartDpi.addEventListener('change', handleDpiChange);
    elements.customDpi.addEventListener('input', updateChartSettings);
    elements.chartWidth.addEventListener('input', handleDimensionChange);
    elements.chartHeight.addEventListener('input', handleDimensionChange);
    elements.chartWidthPx.addEventListener('input', handlePixelDimensionChange);
    elements.chartHeightPx.addEventListener('input', handlePixelDimensionChange);
    elements.aspectRatioLock.addEventListener('change', updateChartSettings);
    elements.chartFormat.addEventListener('change', updateChartSettings);
    
    // Chart type switching
    document.querySelectorAll('.chart-type-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active class from all buttons
            document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
            
            // Add active class to clicked button
            e.target.classList.add('active');
            
            // Update current chart type
            appState.currentChartType = e.target.dataset.chartType;
            
            // Show/hide chart-specific controls
            const chartTypes = ['waveform', 'ieee', 'fft', 'histogram'];
            chartTypes.forEach(type => {
                const controls = document.querySelectorAll(`.${type}-only`);
                controls.forEach(control => {
                    control.style.display = appState.currentChartType === type ? 'block' : 'none';
                });
            });
            
            // Set default chart title if empty
            if (!elements.chartTitle.value) {
                const defaultTitles = {
                    'waveform': 'Flicker Waveform Analysis',
                    'ieee': 'IEEE 1789 Flicker Analysis',
                    'fft': 'Flicker FFT Analysis',
                    'histogram': 'Flicker Frequency Distribution'
                };
                elements.chartTitle.value = defaultTitles[appState.currentChartType] || '';
                appState.chartSettings.title = elements.chartTitle.value;
            }
            
            // Show visualization section if not already visible
            elements.visualizationSection.style.display = 'block';
            
            // Show chart configuration section if we have data
            if (appState.sessionId || appState.manualPoints.length > 0) {
                elements.chartConfigSection.style.display = 'block';
            }
            
            // Update chart
            updateChart();
        });
    });
    
    // Error modal
    elements.closeError.addEventListener('click', () => {
        elements.errorModal.style.display = 'none';
    });
    
    // Manual entry
    elements.addManualPoint.addEventListener('click', handleAddManualPoint);
    
    // Clear all datasets
    if (elements.clearAllDatasets) {
        elements.clearAllDatasets.addEventListener('click', clearAllDatasets);
    }
}

// File Handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        appState.dataLabel = elements.uploadLabel.value || file.name.replace(/\.[^/.]+$/, "");
        processFile(file);
    }
}

// Drag and drop handlers
function handleDragOver(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.stopPropagation();
    elements.uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        appState.dataLabel = elements.uploadLabel.value || file.name.replace(/\.[^/.]+$/, "");
        processFile(file);
    }
}

function processFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading();
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // For waveform and IEEE charts, add to datasets
            if (['waveform', 'ieee'].includes(appState.currentChartType)) {
                addDataset(data.session_id, appState.dataLabel, data.analysis);
            } else {
                // For FFT and histogram, replace current data
                appState.sessionId = data.session_id;
                appState.currentData = data.preview;
            }
            
            // Show visualization section and chart config
            elements.visualizationSection.style.display = 'block';
            elements.chartConfigSection.style.display = 'block';
            
            // Display analysis results if available
            if (data.analysis) {
                displayAnalysisResults(data.analysis);
                elements.analysisResults.style.display = 'block';
            }
            
            // Update chart
            updateChart();
            
            console.log('File processed successfully');
        } else {
            showError(data.error || 'Failed to process file');
        }
    })
    .catch(error => {
        console.error('Error processing file:', error);
        showError('Failed to process file');
    })
    .finally(() => {
        hideLoading();
    });
}

// Pasted Data Handling
function handlePasteData() {
    const csvData = elements.csvPaste.value.trim();
    if (csvData) {
        appState.dataLabel = elements.pasteLabel.value || 'Pasted Data';
        processPastedCSV(csvData);
    } else {
        showError('Please paste CSV data first');
    }
}

// Example Handling
function loadExamples() {
    fetch('/api/examples')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                populateExamplesDropdown(data.examples);
            } else {
                showError('Failed to load examples');
            }
        })
        .catch(error => {
            console.error('Error loading examples:', error);
            showError('Failed to load examples');
        });
}

function populateExamplesDropdown(examples) {
    elements.exampleSelect.innerHTML = '<option value="">Choose an example...</option>';
    
    examples.forEach(example => {
        const option = document.createElement('option');
        // Handle both string format and object format
        const exampleName = typeof example === 'string' ? example : example.name;
        const examplePath = typeof example === 'string' ? example : example.path;
        
        option.value = examplePath;
        option.textContent = exampleName;
        elements.exampleSelect.appendChild(option);
    });
}

function handleExampleSelect() {
    const selectedExample = elements.exampleSelect.value;
    if (selectedExample) {
        // Use custom label if provided, otherwise use the example name
        const selectedText = elements.exampleSelect.options[elements.exampleSelect.selectedIndex].text;
        appState.dataLabel = elements.exampleLabel.value || selectedText;
        loadExample(selectedExample);
    }
}

function loadExample(exampleName) {
    console.log(`Loading example: ${exampleName}`);
    showLoading();
    
    // Properly encode the URL to handle spaces and special characters
    const encodedExampleName = encodeURIComponent(exampleName);
    
    fetch(`/api/example/${encodedExampleName}`)
        .then(response => {
            console.log(`Response status: ${response.status}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Example data received:', data);
            if (data.success) {
                // For waveform and IEEE charts, add to datasets
                if (['waveform', 'ieee'].includes(appState.currentChartType)) {
                    addDataset(data.session_id, appState.dataLabel, data.analysis);
                } else {
                    // For FFT and histogram, replace current data
                    appState.sessionId = data.session_id;
                    appState.currentData = data.preview;
                }
                
                // Show data preview
                displayDataPreview(data.preview);
                
                // Display analysis results
                displayAnalysisResults(data.analysis);
                
                // Show visualization section (which includes config)
                elements.visualizationSection.style.display = 'block';
                elements.chartConfigSection.style.display = 'block';
                elements.analysisResults.style.display = 'block';
                
                // Update chart
                updateChart();
                
                console.log(`Successfully loaded example: ${exampleName}`);
            } else {
                console.error('API returned error:', data.error);
                showError(data.error || 'Failed to load example');
            }
        })
        .catch(error => {
            console.error('Error loading example:', error);
            showError(`Failed to load example: ${error.message}`);
        })
        .finally(() => {
            hideLoading();
        });
}

function processPastedCSV(csvData) {
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
        if (data.success) {
            // For waveform and IEEE charts, add to datasets
            if (['waveform', 'ieee'].includes(appState.currentChartType)) {
                addDataset(data.session_id, appState.dataLabel, data.analysis);
            } else {
                // For FFT and histogram, replace current data
                appState.sessionId = data.session_id;
                appState.currentData = data.preview;
            }
            
            // Show visualization section and chart config
            elements.visualizationSection.style.display = 'block';
            elements.chartConfigSection.style.display = 'block';
            
            // Display analysis results if available
            if (data.analysis) {
                displayAnalysisResults(data.analysis);
                elements.analysisResults.style.display = 'block';
            }
            
            // Update chart
            updateChart();
            
            console.log('CSV data processed successfully');
        } else {
            showError(data.error || 'Failed to process CSV data');
        }
    })
    .catch(error => {
        console.error('Error processing CSV data:', error);
        showError('Failed to process CSV data');
    })
    .finally(() => {
        hideLoading();
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

// Generate chart with multiple datasets
function generateMultiDatasetChart() {
    // For now, use the first dataset and show a message
    if (appState.activeDatasets.length === 0) return;
    
    showLoading();
    
    // Prepare data for multiple datasets
    const datasets = appState.activeDatasets.map(ds => ({
        session_id: ds.sessionId,
        label: ds.label
    }));
    
    // Use first dataset as primary for now
    const primaryDataset = appState.activeDatasets[0];
    appState.sessionId = primaryDataset.sessionId;
    appState.dataLabel = primaryDataset.label;
    
    // Note: This is a temporary implementation. 
    // A proper multi-dataset endpoint would need to be created on the backend
    // For now, we'll use the single dataset endpoint with the first dataset
    
    const config = { ...appState.chartSettings };
    config.data_label = primaryDataset.label;
    
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0) {
        config.manual_points = appState.manualPoints;
    }
    
    fetch(`/api/chart/${appState.currentChartType}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            session_id: primaryDataset.sessionId,
            config: config
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.chart && data.chart.image) {
                elements.chartDisplay.innerHTML = `
                    <div>
                        <img src="${data.chart.image}" alt="Chart" style="max-width: 100%; height: auto;">
                        ${appState.activeDatasets.length > 1 ? 
                            '<p style="text-align: center; color: #666; margin-top: 10px;">Note: Currently showing only the first dataset. Multi-dataset support is coming soon.</p>' : 
                            ''}
                    </div>
                `;
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

// Chart Generation
function updateChart() {
    // Handle multiple datasets for waveform and IEEE charts
    if (['waveform', 'ieee'].includes(appState.currentChartType) && appState.activeDatasets.length > 0) {
        generateMultiDatasetChart();
        return;
    }
    
    // If IEEE chart and we have manual points but no session, use manual-only endpoint
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0 && !appState.sessionId && appState.activeDatasets.length === 0) {
        generateManualOnlyIEEEChart();
        return;
    }
    
    // If IEEE chart with no manual points and no session, show message
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length === 0 && !appState.sessionId && appState.activeDatasets.length === 0) {
        elements.chartDisplay.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>Add manual points or load data to view IEEE 1789-2015 compliance chart</p></div>';
        return;
    }
    
    // If not IEEE chart and no session, show message to load data
    if (!appState.sessionId && appState.activeDatasets.length === 0) {
        elements.chartDisplay.innerHTML = '<div style="text-align: center; padding: 40px; color: #666;"><p>Please load data or select an example to view charts</p></div>';
        return;
    }
    
    showLoading();
    
    // Prepare config with manual points for IEEE charts
    const config = { ...appState.chartSettings };
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0) {
        config.manual_points = appState.manualPoints;
    }
    
    // Include data label for legend
    config.data_label = appState.dataLabel;
    
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
        manual_points: appState.manualPoints,
        data_label: appState.dataLabel
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
    if (elements.loadingSpinner) {
        elements.loadingSpinner.style.display = 'block';
    }
}

function hideLoading() {
    if (elements.loadingSpinner) {
        elements.loadingSpinner.style.display = 'none';
    }
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

// New chart configuration event handlers
function handleDpiChange() {
    const dpiValue = elements.chartDpi.value;
    if (dpiValue === 'custom') {
        elements.customDpiGroup.style.display = 'block';
        appState.chartSettings.export_dpi = parseInt(elements.customDpi.value);
    } else {
        elements.customDpiGroup.style.display = 'none';
        appState.chartSettings.export_dpi = parseInt(dpiValue);
    }
    updateChart();
}

function handleDimensionChange(e) {
    const isWidth = e.target.id === 'chart-width';
    const newValue = parseFloat(e.target.value);
    
    if (appState.chartSettings.aspect_ratio_locked) {
        const currentRatio = appState.chartSettings.width / appState.chartSettings.height;
        
        if (isWidth) {
            appState.chartSettings.width = newValue;
            appState.chartSettings.height = newValue / currentRatio;
            elements.chartHeight.value = appState.chartSettings.height.toFixed(1);
        } else {
            appState.chartSettings.height = newValue;
            appState.chartSettings.width = newValue * currentRatio;
            elements.chartWidth.value = appState.chartSettings.width.toFixed(1);
        }
    } else {
        if (isWidth) {
            appState.chartSettings.width = newValue;
        } else {
            appState.chartSettings.height = newValue;
        }
    }
    
    updateChart();
}

function updateChartSettings() {
    // Update all chart settings from form elements
    appState.chartSettings.title = elements.chartTitle.value;
    appState.chartSettings.font = elements.fontFamily.value;
    appState.chartSettings.title_size = parseInt(elements.titleFontSize.value);
    appState.chartSettings.axis_label_size = parseInt(elements.axisFontSize.value);
    appState.chartSettings.legend_size = parseInt(elements.legendFontSize.value);
    appState.chartSettings.show_metrics = elements.showMetrics.checked;
    appState.chartSettings.show_standards = elements.showStandards.checked;
    appState.chartSettings.show_legend = elements.showLegend.checked;
    appState.chartSettings.legend_position = elements.legendPosition.value;
    appState.chartSettings.format = elements.chartFormat.value;
    appState.chartSettings.aspect_ratio_locked = elements.aspectRatioLock.checked;
    
    // Update DPI if custom is selected
    if (elements.chartDpi.value === 'custom') {
        appState.chartSettings.export_dpi = parseInt(elements.customDpi.value);
    }
    
    updateChart();
}

// Input tab switching
function switchInputTab(tabName) {
    // Update tab buttons
    elements.inputTabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    
    // Update content visibility
    elements.inputContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabName}-content`);
    });
    
    // Load examples if switching to examples tab and dropdown is empty
    if (tabName === 'examples' && elements.exampleSelect.children.length <= 1) {
        loadExamples();
    }
}

// Resolution type switching
function handleResolutionTypeChange() {
    const resolutionType = elements.resolutionType.value;
    appState.chartSettings.resolution_type = resolutionType;
    
    if (resolutionType === 'dpi') {
        elements.dpiSettings.style.display = 'block';
        elements.pixelSettings.style.display = 'none';
    } else {
        elements.dpiSettings.style.display = 'none';
        elements.pixelSettings.style.display = 'block';
    }
    
    updateChart();
}

// Pixel dimension handling
function handlePixelDimensionChange(e) {
    const isWidth = e.target.id === 'chart-width-px';
    const newValue = parseInt(e.target.value);
    
    if (appState.chartSettings.aspect_ratio_locked) {
        const currentRatio = appState.chartSettings.width_px / appState.chartSettings.height_px;
        
        if (isWidth) {
            appState.chartSettings.width_px = newValue;
            appState.chartSettings.height_px = Math.round(newValue / currentRatio);
            elements.chartHeightPx.value = appState.chartSettings.height_px;
        } else {
            appState.chartSettings.height_px = newValue;
            appState.chartSettings.width_px = Math.round(newValue * currentRatio);
            elements.chartWidthPx.value = appState.chartSettings.width_px;
        }
    } else {
        if (isWidth) {
            appState.chartSettings.width_px = newValue;
        } else {
            appState.chartSettings.height_px = newValue;
        }
    }
    
    updateChart();
}