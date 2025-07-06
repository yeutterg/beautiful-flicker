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
        font: 'sans-serif',
        title_size: 16,
        title_bold: true,
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
        width_px: 3000, // Default IEEE chart size
        height_px: 2000,
        resolution_type: 'pixels', // Default to pixels
        aspect_ratio_locked: true
    },
    exportSettings: {
        format: 'png',
        transparent_bg: false,
        export_dpi: 300,
        size_preset: 'auto'
    },
    currentChartType: 'ieee' // Start with IEEE 1789 as first chart
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
    manualColor: document.getElementById('manual-color'),
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
    initializeDefaults();
    
    // Show visualization section immediately with IEEE 1789 selected
    elements.visualizationSection.style.display = 'block';
    
    // Set IEEE 1789 as active
    document.querySelector('.chart-type-btn[data-chart-type="ieee"]').classList.add('active');
});

// Initialize default values
function initializeDefaults() {
    // Set default title for initial chart type
    const defaultTitles = {
        'waveform': 'Flicker Waveform Analysis',
        'ieee': 'IEEE 1789 Flicker Analysis',
        'fft': 'Flicker FFT Analysis',
        'histogram': 'Flicker Frequency Distribution'
    };
    
    if (!elements.chartTitle.value) {
        elements.chartTitle.value = defaultTitles[appState.currentChartType] || '';
        appState.chartSettings.title = elements.chartTitle.value;
    }
    
    // Initialize chart-specific controls visibility
    const chartTypes = ['waveform', 'ieee', 'fft', 'histogram'];
    chartTypes.forEach(type => {
        const controls = document.querySelectorAll(`.${type}-only`);
        controls.forEach(control => {
            control.style.display = appState.currentChartType === type ? 'block' : 'none';
        });
    });
    
    // Set random initial color for manual points
    updateManualPointColor();
}

// Generate a random color for manual points
function getRandomColor() {
    const colors = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

function updateManualPointColor() {
    if (elements.manualColor) {
        elements.manualColor.value = getRandomColor();
    }
}

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
    if (appState.activeDatasets.length > 0 && elements.activeDatasetsSection) {
        elements.activeDatasetsSection.style.display = 'block';
    }
    
    // Show success feedback
    showSuccess(`Added dataset: ${label}`);
}

function removeDataset(index) {
    appState.activeDatasets.splice(index, 1);
    updateDatasetsList();
    
    // Hide section if no datasets
    if (appState.activeDatasets.length === 0 && elements.activeDatasetsSection) {
        elements.activeDatasetsSection.style.display = 'none';
    }
    
    // Update Added Points section
    updateAddedPointsSection();
    
    // Update analysis table
    updateAnalysisTable();
    
    // Update chart
    updateChart();
}

// Make removeDataset globally accessible
window.removeDataset = removeDataset;

function clearAllDatasets() {
    if (appState.activeDatasets.length === 0) return;
    
    if (confirm(`Are you sure you want to remove all ${appState.activeDatasets.length} datasets?`)) {
        const count = appState.activeDatasets.length;
        appState.activeDatasets = [];
        updateDatasetsList();
        if (elements.activeDatasetsSection) {
            elements.activeDatasetsSection.style.display = 'none';
        }
        updateChart();
        showSuccess(`Removed ${count} datasets`);
    }
}

function updateDatasetsList() {
    if (!elements.datasetsList) return;
    
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
    
    // Update data label when custom example label changes
    if (elements.exampleLabel) {
        elements.exampleLabel.addEventListener('input', () => {
            // Update data label if an example is selected
            if (elements.exampleSelect.value) {
                const selectedText = elements.exampleSelect.options[elements.exampleSelect.selectedIndex].text;
                appState.dataLabel = elements.exampleLabel.value || selectedText;
            }
        });
    }
    
    // Chart configuration
    if (elements.chartTitle) elements.chartTitle.addEventListener('input', updateChartSettings);
    if (elements.fontFamily) elements.fontFamily.addEventListener('change', updateChartSettings);
    if (elements.titleFontSize) elements.titleFontSize.addEventListener('input', updateChartSettings);
    if (elements.axisFontSize) elements.axisFontSize.addEventListener('input', updateChartSettings);
    if (elements.legendFontSize) elements.legendFontSize.addEventListener('input', updateChartSettings);
    if (elements.showMetrics) elements.showMetrics.addEventListener('change', updateChartSettings);
    if (elements.showStandards) elements.showStandards.addEventListener('change', updateChartSettings);
    if (elements.showLegend) elements.showLegend.addEventListener('change', updateChartSettings);
    if (elements.legendPosition) elements.legendPosition.addEventListener('change', updateChartSettings);
    
    // Export configuration
    if (elements.resolutionType) elements.resolutionType.addEventListener('change', handleResolutionTypeChange);
    if (elements.chartDpi) elements.chartDpi.addEventListener('change', handleDpiChange);
    if (elements.customDpi) elements.customDpi.addEventListener('input', updateChartSettings);
    if (elements.chartWidth) elements.chartWidth.addEventListener('input', handleDimensionChange);
    if (elements.chartHeight) elements.chartHeight.addEventListener('input', handleDimensionChange);
    if (elements.chartWidthPx) elements.chartWidthPx.addEventListener('input', handlePixelDimensionChange);
    if (elements.chartHeightPx) elements.chartHeightPx.addEventListener('input', handlePixelDimensionChange);
    if (elements.aspectRatioLock) elements.aspectRatioLock.addEventListener('change', updateChartSettings);
    if (elements.chartFormat) elements.chartFormat.addEventListener('change', updateChartSettings);
    
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
            
            // Set appropriate default chart title for chart type
            const defaultTitles = {
                'waveform': 'Flicker Waveform Analysis',
                'ieee': 'IEEE 1789 Flicker Analysis',
                'fft': 'Flicker FFT Analysis',
                'histogram': 'Flicker Frequency Distribution'
            };
            
            // Only set default if current title is empty or is a default title from another chart type
            const currentTitle = elements.chartTitle.value;
            const isDefaultTitle = Object.values(defaultTitles).includes(currentTitle);
            
            if (!currentTitle || isDefaultTitle) {
                elements.chartTitle.value = defaultTitles[appState.currentChartType] || '';
                appState.chartSettings.title = elements.chartTitle.value;
            }
            
            // Show visualization section if not already visible
            elements.visualizationSection.style.display = 'block';
            
            // Show chart configuration section if we have data
            if (appState.sessionId || appState.activeDatasets.length > 0 || appState.manualPoints.length > 0) {
                elements.chartConfigSection.style.display = 'block';
            }
            
            // Show info about chart type capabilities
            if (appState.currentChartType === 'ieee' || appState.currentChartType === 'waveform') {
                if (appState.activeDatasets.length > 1) {
                    // Multi-dataset support message is already handled in generateMultiDatasetChart
                }
            } else {
                // FFT and histogram only support single dataset
                if (appState.activeDatasets.length > 1) {
                    showSuccess(`Switched to ${appState.currentChartType.toUpperCase()} - showing only the most recent dataset`);
                }
            }
            
            // Update chart
            updateChart();
        });
    });
    
    // Error modal
    if (elements.closeError) {
        elements.closeError.addEventListener('click', () => {
            if (elements.errorModal) {
                elements.errorModal.style.display = 'none';
            }
        });
    }
    
    // Close modal when clicking outside
    if (elements.errorModal) {
        elements.errorModal.addEventListener('click', (e) => {
            if (e.target === elements.errorModal) {
                elements.errorModal.style.display = 'none';
            }
        });
    }
    
    // Manual entry
    if (elements.addManualPoint) {
        elements.addManualPoint.addEventListener('click', handleAddManualPoint);
    }
    
    // Clear all datasets
    if (elements.clearAllDatasets) {
        elements.clearAllDatasets.addEventListener('click', clearAllDatasets);
    }
    
    // Export chart
    const exportButton = document.getElementById('exportChart');
    if (exportButton) {
        exportButton.addEventListener('click', handleExport);
    }
    
    // Update chart button
    const updateButton = document.getElementById('updateChart');
    if (updateButton) {
        updateButton.addEventListener('click', () => {
            updateChartSettings();
            showSuccess('Chart updated with new settings');
        });
    }
    
    // Update chart from points button
    const updateFromPointsBtn = document.getElementById('updateChartFromPoints');
    if (updateFromPointsBtn) {
        updateFromPointsBtn.addEventListener('click', () => {
            updateChart();
            showSuccess('Chart updated');
        });
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
            
            // Display data preview and analysis results if available
            if (data.preview) {
                displayDataPreview(data.preview);
            }
            
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
            
            // Display data preview and analysis results if available
            if (data.preview) {
                displayDataPreview(data.preview);
            }
            
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
    // Only show in the collapsible analysis results in the visualization area
    const analysisWrapper = document.getElementById('analysisResultsWrapper');
    const analysisContent = document.querySelector('#analysisResultsWrapper .analysis-results-content');
    
    if (analysisWrapper && analysisContent) {
        // Update the table whenever a new dataset is added
        updateAnalysisTable();
    }
}

// Update the analysis table with all data points
function updateAnalysisTable() {
    const analysisWrapper = document.getElementById('analysisResultsWrapper');
    const analysisContent = document.querySelector('#analysisResultsWrapper .analysis-results-content');
    
    if (!analysisWrapper || !analysisContent) return;
    
    // Combine all data sources
    const allDataPoints = [];
    
    // Add datasets
    appState.activeDatasets.forEach((dataset, index) => {
        allDataPoints.push({
            type: 'dataset',
            label: dataset.label,
            frequency: dataset.analysis.frequency,
            percentFlicker: dataset.analysis.percent_flicker,
            flickerIndex: dataset.analysis.flicker_index,
            rmsVariation: dataset.analysis.rms_variation,
            ieee: dataset.analysis.ieee_1789_2015,
            ja8: dataset.analysis.california_ja8_2019,
            well: dataset.analysis.well_standard_v2,
            color: '#1f77b4' // Default color for datasets
        });
    });
    
    // Add manual points
    appState.manualPoints.forEach(point => {
        allDataPoints.push({
            type: 'manual',
            label: point.label,
            frequency: point.frequency,
            percentFlicker: point.modulation,
            flickerIndex: '--',
            rmsVariation: '--',
            ieee: 'Manual Point',
            ja8: '--',
            well: '--',
            color: point.color
        });
    });
    
    if (allDataPoints.length === 0) {
        analysisWrapper.style.display = 'none';
        return;
    }
    
    analysisWrapper.style.display = 'block';
    
    // Build table HTML
    let tableHTML = `
        <table class="analysis-table">
            <thead>
                <tr>
                    <th>Data Point</th>
                    <th>Frequency (Hz)</th>
                    <th>% Flicker</th>
                    <th>Flicker Index</th>
                    <th>RMS Variation</th>
                    <th>IEEE 1789-2015</th>
                    <th>CA JA8</th>
                    <th>WELL v2</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    allDataPoints.forEach(point => {
        const ieeeClass = getStatusClass(point.ieee);
        const ja8Class = point.ja8 === true || point.ja8 === 'Pass' ? 'pass' : (point.ja8 === false || point.ja8 === 'Fail' ? 'fail' : '');
        const wellClass = point.well === true || point.well === 'Pass' ? 'pass' : (point.well === false || point.well === 'Fail' ? 'fail' : '');
        
        tableHTML += `
            <tr>
                <td>
                    <span class="point-color" style="display: inline-block; width: 12px; height: 12px; background-color: ${point.color}; border: 1px solid #000; margin-right: 5px;"></span>
                    ${point.label}
                </td>
                <td>${point.frequency}</td>
                <td>${point.percentFlicker}${typeof point.percentFlicker === 'number' ? '%' : ''}</td>
                <td>${point.flickerIndex}</td>
                <td>${point.rmsVariation}${point.rmsVariation !== '--' && point.rmsVariation != null ? '%' : ''}</td>
                <td class="result-status" data-status="${ieeeClass}">${point.ieee}</td>
                <td class="result-status" data-status="${ja8Class}">${point.ja8 === true ? 'Pass' : (point.ja8 === false ? 'Fail' : point.ja8)}</td>
                <td class="result-status" data-status="${wellClass}">${point.well === true ? 'Pass' : (point.well === false ? 'Fail' : point.well)}</td>
            </tr>
        `;
    });
    
    tableHTML += `
            </tbody>
        </table>
    `;
    
    analysisContent.innerHTML = tableHTML;
}

function getStatusClass(result) {
    if (result === 'Pass' || result === 'No Risk') {
        return result === 'Pass' ? 'pass' : 'no-risk';
    } else if (result === 'Low Risk') {
        return 'low-risk';
    } else if (result === 'Fail' || result === 'High Risk') {
        return result === 'Fail' ? 'fail' : 'high-risk';
    }
    return '';
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
    if (elements.chartTitle) appState.chartSettings.title = elements.chartTitle.value;
    if (elements.fontFamily) appState.chartSettings.font = elements.fontFamily.value;
    appState.chartSettings.show_metrics = elements.showMetrics ? elements.showMetrics.checked : true;
    appState.chartSettings.show_standards = elements.showStandards ? elements.showStandards.checked : true;
    appState.chartSettings.show_legend = elements.showLegend ? elements.showLegend.checked : true;
    
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
    config.data_color = primaryDataset.color || '#1f77b4';
    
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
    // Always show visualization section if chart type is selected
    if (elements.visualizationSection) {
        elements.visualizationSection.style.display = 'block';
    }
    
    // Show chart config section if we have any data
    const hasData = appState.sessionId || appState.activeDatasets.length > 0 || appState.manualPoints.length > 0;
    if (hasData && elements.chartConfigSection) {
        elements.chartConfigSection.style.display = 'block';
    }
    
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
    
    // Include data label and color for legend
    config.data_label = appState.dataLabel;
    
    // If we have an active dataset, use its color
    if (appState.activeDatasets.length > 0) {
        config.data_color = appState.activeDatasets[0].color || '#1f77b4';
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
    if (!appState.sessionId && appState.activeDatasets.length === 0 && appState.manualPoints.length === 0) {
        showError('No data to export. Please load data, add manual points, or select an example first.');
        return;
    }
    
    // Get current resolution settings
    const resolutionType = elements.resolutionType ? elements.resolutionType.value : 'pixels';
    const config = { ...appState.chartSettings };
    
    if (resolutionType === 'pixels') {
        config.resolution_type = 'pixels';
        config.width_px = elements.chartWidthPx ? parseInt(elements.chartWidthPx.value) : 1200;
        config.height_px = elements.chartHeightPx ? parseInt(elements.chartHeightPx.value) : 800;
    } else {
        config.resolution_type = 'dpi';
        config.width = elements.chartWidth ? parseFloat(elements.chartWidth.value) : 10;
        config.height = elements.chartHeight ? parseFloat(elements.chartHeight.value) : 6;
        if (elements.chartDpi && elements.chartDpi.value === 'custom' && elements.customDpi) {
            config.export_dpi = parseInt(elements.customDpi.value);
        } else if (elements.chartDpi) {
            config.export_dpi = parseInt(elements.chartDpi.value);
        } else {
            config.export_dpi = 300;
        }
    }
    
    config.format = elements.chartFormat ? elements.chartFormat.value : 'png';
    const transparentCheckbox = document.getElementById('transparentBg');
    config.transparent_bg = transparentCheckbox ? transparentCheckbox.checked : false;
    
    // Include data label and color for export
    if (appState.activeDatasets.length > 0) {
        config.data_label = appState.activeDatasets[0].label;
        config.data_color = appState.activeDatasets[0].color || '#1f77b4';
    } else if (appState.dataLabel) {
        config.data_label = appState.dataLabel;
    }
    
    // Include manual points for IEEE charts
    if (appState.currentChartType === 'ieee' && appState.manualPoints.length > 0) {
        config.manual_points = appState.manualPoints;
    }
    
    // Skip the exportConfig part as it's not needed with the new config approach
    
    showLoading();
    
    fetch(`/api/export/${config.format}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: appState.sessionId || (appState.activeDatasets.length > 0 ? appState.activeDatasets[0].sessionId : null),
            chart_type: appState.currentChartType,
            export_config: config
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
        a.download = `flicker_${appState.currentChartType}.${config.format}`;
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
    try {
        if (elements.errorMessage) {
            elements.errorMessage.textContent = message;
        }
        if (elements.errorModal) {
            elements.errorModal.style.display = 'flex';
        }
    } catch (e) {
        console.error('Error showing error modal:', e);
        console.error('Original error message:', message);
        // Fallback to alert if modal fails
        alert(message);
    }
}

function showSuccess(message) {
    // Create a temporary success message
    const successDiv = document.createElement('div');
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #2D6A2D;
        color: white;
        padding: 1rem;
        border-radius: 4px;
        z-index: 1000;
        max-width: 300px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-family: var(--font-primary);
    `;
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    
    // Remove after 3 seconds
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.parentNode.removeChild(successDiv);
        }
    }, 3000);
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
    const color = elements.manualColor.value;
    
    if (!frequency || !modulation) {
        showError('Please enter both frequency and modulation values');
        return;
    }
    
    if (frequency < 1 || frequency > 100000) {
        showError('Frequency must be between 1 and 100000 Hz');
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
        label: label,
        color: color
    };
    
    appState.manualPoints.push(point);
    
    // Clear inputs (but keep color for convenience)
    elements.manualFrequency.value = '';
    elements.manualModulation.value = '';
    elements.manualLabel.value = '';
    // Note: Keeping color unchanged for user convenience
    
    // Update display
    updateManualPointsDisplay();
    
    // Set a new random color for the next point
    updateManualPointColor();
    
    // Show success feedback
    showSuccess(`Added manual point: ${label} (${frequency} Hz, ${modulation}%)`);
    
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
    // Update manual points in the input section
    if (appState.manualPoints.length === 0) {
        elements.manualPointsList.style.display = 'none';
    } else {
        elements.manualPointsList.style.display = 'block';
        elements.manualPointsContainer.innerHTML = '';
        
        appState.manualPoints.forEach(point => {
            const item = document.createElement('div');
            item.className = 'manual-point-item';
            item.innerHTML = `
                <div class="manual-point-info">
                    <div class="manual-point-color" style="background-color: ${point.color}"></div>
                    <div class="manual-point-details">
                        <strong>${point.label}</strong>: ${point.frequency} Hz, ${point.modulation}%
                    </div>
                </div>
                <div class="manual-point-controls">
                    <input type="color" value="${point.color}" onchange="updateManualPointColor(${point.id}, this.value)" class="manual-point-color-picker" title="Change color">
                    <button class="manual-point-remove" onclick="removeManualPoint(${point.id})">×</button>
                </div>
            `;
            elements.manualPointsContainer.appendChild(item);
        });
    }
    
    // Update Added Points section in visualization area
    updateAddedPointsSection();
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

function updateManualPointColor(pointId, newColor) {
    const point = appState.manualPoints.find(p => p.id === pointId);
    if (point) {
        point.color = newColor;
        updateManualPointsDisplay();
        if (appState.currentChartType === 'ieee') {
            updateChart();
        }
        showSuccess(`Updated color for ${point.label}`);
    }
}

// Make functions globally accessible
window.removeManualPoint = removeManualPoint;
window.updateManualPointColor = updateManualPointColor;

// Update Added Points section in visualization area
function updateAddedPointsSection() {
    const addedPointsSection = document.getElementById('addedPointsSection');
    const addedPointsList = document.getElementById('addedPointsList');
    
    if (!addedPointsSection || !addedPointsList) return;
    
    // Show/hide section based on whether we have points
    if (appState.manualPoints.length === 0 && appState.activeDatasets.length === 0) {
        addedPointsSection.style.display = 'none';
        return;
    }
    
    addedPointsSection.style.display = 'block';
    addedPointsList.innerHTML = '';
    
    // Add datasets
    appState.activeDatasets.forEach((dataset, index) => {
        const item = document.createElement('div');
        item.className = 'point-item';
        item.dataset.type = 'dataset';
        item.dataset.datasetIndex = index;
        item.setAttribute('data-dataset-index', index);
        item.draggable = true;
        
        // Default color for datasets
        const color = dataset.color || '#1f77b4';
        
        item.innerHTML = `
            <input type="checkbox" class="point-checkbox" checked onchange="toggleDatasetVisibility(${index})">
            <input type="color" value="${color}" onchange="updateDatasetColor(${index}, this.value)" class="point-color-picker" title="Change color">
            <div class="point-info">
                <input type="text" value="${dataset.label}" onchange="updateDatasetLabel(${index}, this.value)" class="point-label-input" style="font-weight: bold; border: none; background: transparent; width: 100%;">
                <br><small>${dataset.analysis.frequency} Hz, ${dataset.analysis.percent_flicker}%</small>
            </div>
            <div class="point-controls">
                <button class="btn btn-small" onclick="removeDataset(${index})">Remove</button>
            </div>
        `;
        addedPointsList.appendChild(item);
    });
    
    // Add manual points
    appState.manualPoints.forEach((point, index) => {
        const item = document.createElement('div');
        item.className = 'point-item';
        item.dataset.type = 'manual';
        item.dataset.manualId = point.id;
        item.setAttribute('data-manual-id', point.id);
        item.draggable = true;
        item.innerHTML = `
            <input type="checkbox" class="point-checkbox" checked onchange="toggleManualPointVisibility(${point.id})">
            <input type="color" value="${point.color}" onchange="updateManualPointColor(${point.id}, this.value)" class="point-color-picker" title="Change color">
            <div class="point-info">
                <input type="text" value="${point.label}" onchange="updateManualPointLabel(${point.id}, this.value)" class="point-label-input" style="font-weight: bold; border: none; background: transparent; width: 100%;">
                <br><small>${point.frequency} Hz, ${point.modulation}%</small>
            </div>
            <div class="point-controls">
                <button class="btn btn-small" onclick="removeManualPoint(${point.id})">Remove</button>
            </div>
        `;
        addedPointsList.appendChild(item);
    });
    
    // Set up drag and drop
    setupPointsDragAndDrop();
}

// Toggle dataset visibility (placeholder for future implementation)
function toggleDatasetVisibility(index) {
    // TODO: Implement dataset visibility toggle
    showSuccess('Dataset visibility toggle coming soon');
}

// Toggle manual point visibility (placeholder for future implementation)
function toggleManualPointVisibility(pointId) {
    // TODO: Implement manual point visibility toggle
    showSuccess('Point visibility toggle coming soon');
}

// Set up drag and drop for reordering points
function setupPointsDragAndDrop() {
    const pointItems = document.querySelectorAll('.point-item');
    let draggedItem = null;
    
    pointItems.forEach(item => {
        item.addEventListener('dragstart', (e) => {
            draggedItem = e.target;
            e.target.classList.add('dragging');
        });
        
        item.addEventListener('dragend', (e) => {
            e.target.classList.remove('dragging');
        });
        
        item.addEventListener('dragover', (e) => {
            e.preventDefault();
            const draggingItem = document.querySelector('.dragging');
            const container = document.getElementById('addedPointsList');
            const afterElement = getDragAfterElement(container, e.clientY);
            
            if (afterElement == null) {
                container.appendChild(draggingItem);
            } else {
                container.insertBefore(draggingItem, afterElement);
            }
        });
        
        item.addEventListener('drop', (e) => {
            e.preventDefault();
            // Reorder the actual data arrays based on the new visual order
            reorderDataBasedOnDOM();
        });
    });
}

// Get the element after which to insert the dragged item
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.point-item:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Reorder data arrays based on the new DOM order
function reorderDataBasedOnDOM() {
    const pointItems = document.querySelectorAll('.point-item');
    const newActiveDatasets = [];
    const newManualPoints = [];
    
    pointItems.forEach(item => {
        const datasetIndex = parseInt(item.getAttribute('data-dataset-index'));
        const manualId = parseInt(item.getAttribute('data-manual-id'));
        
        if (!isNaN(datasetIndex) && appState.activeDatasets[datasetIndex]) {
            newActiveDatasets.push(appState.activeDatasets[datasetIndex]);
        } else if (!isNaN(manualId)) {
            const manualPoint = appState.manualPoints.find(p => p.id === manualId);
            if (manualPoint) {
                newManualPoints.push(manualPoint);
            }
        }
    });
    
    // Update the state arrays
    appState.activeDatasets = newActiveDatasets;
    appState.manualPoints = newManualPoints;
    
    // Update the chart and analysis table
    updateChart();
    updateAnalysisTable();
}

// Update dataset color
function updateDatasetColor(index, newColor) {
    if (appState.activeDatasets[index]) {
        appState.activeDatasets[index].color = newColor;
        updateChart();
        updateAnalysisTable();
        showSuccess(`Updated color for ${appState.activeDatasets[index].label}`);
    }
}

// Update dataset label
function updateDatasetLabel(index, newLabel) {
    if (appState.activeDatasets[index]) {
        appState.activeDatasets[index].label = newLabel;
        updateChart();
        updateAnalysisTable();
    }
}

// Update manual point label
function updateManualPointLabel(pointId, newLabel) {
    const point = appState.manualPoints.find(p => p.id === pointId);
    if (point) {
        point.label = newLabel;
        updateChart();
        updateAnalysisTable();
    }
}

// Make new functions globally accessible
window.toggleDatasetVisibility = toggleDatasetVisibility;
window.toggleManualPointVisibility = toggleManualPointVisibility;
window.updateDatasetColor = updateDatasetColor;
window.updateDatasetLabel = updateDatasetLabel;
window.updateManualPointLabel = updateManualPointLabel;

// Toggle collapsible sections
function toggleCollapsible(button) {
    const content = button.nextElementSibling;
    const icon = button.querySelector('.collapsible-icon');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.classList.add('active');
        icon.textContent = '▼';
    } else {
        content.style.display = 'none';
        button.classList.remove('active');
        icon.textContent = '▶';
    }
}

// Make toggleCollapsible globally accessible
window.toggleCollapsible = toggleCollapsible;

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
            if (elements.chartHeight) elements.chartHeight.value = appState.chartSettings.height.toFixed(1);
        } else {
            appState.chartSettings.height = newValue;
            appState.chartSettings.width = newValue * currentRatio;
            if (elements.chartWidth) elements.chartWidth.value = appState.chartSettings.width.toFixed(1);
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
    if (elements.chartTitle) appState.chartSettings.title = elements.chartTitle.value;
    if (elements.fontFamily) appState.chartSettings.font = elements.fontFamily.value;
    if (elements.titleFontSize) appState.chartSettings.title_size = parseInt(elements.titleFontSize.value);
    if (elements.axisFontSize) appState.chartSettings.axis_label_size = parseInt(elements.axisFontSize.value);
    if (elements.legendFontSize) appState.chartSettings.legend_size = parseInt(elements.legendFontSize.value);
    if (elements.showMetrics) appState.chartSettings.show_metrics = elements.showMetrics.checked;
    if (elements.showStandards) appState.chartSettings.show_standards = elements.showStandards.checked;
    if (elements.showLegend) appState.chartSettings.show_legend = elements.showLegend.checked;
    if (elements.legendPosition) appState.chartSettings.legend_position = elements.legendPosition.value;
    if (elements.chartFormat) appState.chartSettings.format = elements.chartFormat.value;
    if (elements.aspectRatioLock) appState.chartSettings.aspect_ratio_locked = elements.aspectRatioLock.checked;
    
    // Update bold title setting
    const titleBoldCheckbox = document.getElementById('title-bold');
    if (titleBoldCheckbox) {
        appState.chartSettings.title_bold = titleBoldCheckbox.checked;
    }
    
    // Update DPI if custom is selected
    if (elements.chartDpi && elements.chartDpi.value === 'custom' && elements.customDpi) {
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
            if (elements.chartHeightPx) elements.chartHeightPx.value = appState.chartSettings.height_px;
        } else {
            appState.chartSettings.height_px = newValue;
            appState.chartSettings.width_px = Math.round(newValue * currentRatio);
            if (elements.chartWidthPx) elements.chartWidthPx.value = appState.chartSettings.width_px;
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