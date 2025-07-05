"""Visualization module for Beautiful Flicker Flask app."""

import sys
import os
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
# Note: SVG export is handled by fig.savefig() which doesn't require explicit backend import
from matplotlib.backends.backend_pdf import PdfPages
from typing import Dict, Any, Optional, Tuple, List

# Import from the src directory (copied to /app/src/ in Docker)
from src.plot import ieee_par_1789_graph


class ChartGenerator:
    """Handles chart generation for flicker data visualization."""
    
    def __init__(self):
        """Initialize the chart generator with default settings."""
        self.default_figsize = (10, 6)
        self.default_dpi = 100
        
        # Brutalist color scheme
        self.colors = {
            'background': '#FAFAF8',
            'text': '#0A0A0A',
            'accent': '#4A4A4A',
            'grid': '#E0E0E0',
            'data': '#2A2A2A'
        }
    
    def generate_waveform(self, data: np.ndarray, analysis: Dict[str, Any], 
                         config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a waveform chart.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            analysis: Analysis results dictionary
            config: Chart configuration dictionary
            
        Returns:
            Dictionary with chart data including base64 encoded image
        """
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        
        # Apply brutalist styling
        self._apply_brutalist_style(fig, ax)
        
        # Plot waveform
        time_ms = data[:, 0] * 1000  # Convert to milliseconds
        voltage_normalized = self._normalize_voltage(data[:, 1])
        
        ax.plot(time_ms, voltage_normalized, color=self.colors['data'], linewidth=2)
        
        # Configure axes
        ax.set_xlabel('Time (ms)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Light Output', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, time_ms[-1])
        ax.set_ylim(0, 1)
        
        # Apply consistent font settings
        self._apply_font_settings(ax, config)
        
        # Add title if configured
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        # Add overlays if configured
        if config.get('show_metrics', True):
            self._add_metrics_overlay(ax, analysis)
        
        if config.get('show_standards', True):
            self._add_standards_overlay(ax, analysis)
        
        # Configure legend if enabled
        if config.get('show_legend', False) and config.get('legend_items'):
            self._configure_legend(ax, config)
        
        plt.tight_layout()
        
        # Convert to base64
        img_data = self._fig_to_base64(fig)
        plt.close(fig)
        
        return {
            'type': 'waveform',
            'image': img_data,
            'format': 'png'
        }
    
    def generate_ieee_plot(self, analysis: Dict[str, Any], 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate IEEE PAR 1789-2015 compliance plot.
        
        Args:
            analysis: Analysis results dictionary
            config: Chart configuration dictionary
            
        Returns:
            Dictionary with chart data including base64 encoded image
        """
        # Validate that required fields exist
        required_fields = ['frequency', 'percent_flicker']
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing analysis fields for IEEE plot: {missing_fields}")
        
        # Prepare data for IEEE plot
        freq = analysis['frequency']
        pct_flicker = analysis['percent_flicker'] / 100  # Convert to decimal
        # Use data_label for legend, fallback to 'Measurement'
        name = config.get('data_label', 'Measurement')
        
        # Create plot data list
        plot_data = [(freq, pct_flicker, name)]
        
        # Add manual points if provided
        manual_points = config.get('manual_points', [])
        for point in manual_points:
            if 'frequency' in point and 'modulation' in point:
                manual_freq = point['frequency']
                manual_mod = point['modulation'] / 100  # Convert to decimal
                manual_label = point.get('label', 'Manual Point')
                plot_data.append((manual_freq, manual_mod, manual_label))
        
        # Generate the plot using the original library's exact implementation
        fig = self._generate_ieee_plot_original(plot_data, config)
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return {
            'type': 'ieee',
            'image': f'data:image/png;base64,{image_base64}',
            'title': name or 'IEEE PAR 1789-2015 Compliance'
        }
    
    def generate_ieee_plot_manual_only(self, manual_points: List[Dict[str, Any]], 
                                      config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate IEEE PAR 1789-2015 compliance plot with only manual points.
        
        Args:
            manual_points: List of manual point dictionaries
            config: Chart configuration dictionary
            
        Returns:
            Dictionary with chart data including base64 encoded image
        """
        # Prepare data for IEEE plot (only manual points)
        plot_data = []
        
        for point in manual_points:
            if 'frequency' in point and 'modulation' in point:
                manual_freq = point['frequency']
                manual_mod = point['modulation'] / 100  # Convert to decimal
                manual_label = point.get('label', 'Manual Point')
                plot_data.append((manual_freq, manual_mod, manual_label))
        
        if not plot_data:
            raise ValueError("No valid manual points provided")
        
        # Generate the plot using the original library's exact implementation
        fig = self._generate_ieee_plot_original(plot_data, config)
        
        # Convert to base64
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        
        return {
            'type': 'ieee',
            'image': f'data:image/png;base64,{image_base64}',
            'title': 'IEEE PAR 1789-2015 Compliance (Manual Points)'
        }
    
    def generate_fft_spectrum(self, data: np.ndarray, 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FFT spectrum plot.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            config: Chart configuration dictionary
            
        Returns:
            Dictionary with chart data including base64 encoded image
        """
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        
        # Apply brutalist styling
        self._apply_brutalist_style(fig, ax)
        
        # Perform FFT
        values = data[:, 1]
        time_diff = data[1, 0] - data[0, 0]
        framerate = int(1 / time_diff)
        
        # Remove DC component
        values = values - np.mean(values)
        
        # Perform FFT
        fft_values = np.fft.fft(values)
        fft_freq = np.fft.fftfreq(len(values), 1/framerate)
        
        # Get positive frequencies only
        positive_freq_idx = fft_freq > 0
        frequencies = fft_freq[positive_freq_idx]
        magnitudes = np.abs(fft_values[positive_freq_idx])
        
        # Normalize and limit frequency range
        magnitudes = magnitudes / np.max(magnitudes)
        freq_limit = min(3000, np.max(frequencies))
        relevant_idx = frequencies <= freq_limit
        
        # Plot spectrum
        ax.plot(frequencies[relevant_idx], magnitudes[relevant_idx], 
               color=self.colors['data'], linewidth=2)
        
        # Configure axes
        ax.set_xlabel('Frequency (Hz)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Magnitude (normalized)', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, freq_limit)
        ax.set_ylim(0, 1.1)
        
        # Add title if configured
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Convert to base64
        img_data = self._fig_to_base64(fig)
        plt.close(fig)
        
        return {
            'type': 'fft',
            'image': img_data,
            'format': 'png'
        }
    
    def generate_histogram(self, data: np.ndarray, 
                          config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate histogram of light output values.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            config: Chart configuration dictionary
            
        Returns:
            Dictionary with chart data including base64 encoded image
        """
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        
        # Apply brutalist styling
        self._apply_brutalist_style(fig, ax)
        
        # Normalize voltage values
        voltage_normalized = self._normalize_voltage(data[:, 1])
        
        # Create histogram
        n_bins = config.get('n_bins', 50)
        ax.hist(voltage_normalized, bins=n_bins, color=self.colors['data'], 
                edgecolor=self.colors['accent'], alpha=0.8)
        
        # Configure axes
        ax.set_xlabel('Light Output', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Count', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, 1)
        
        # Add title if configured
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        plt.tight_layout()
        
        # Convert to base64
        img_data = self._fig_to_base64(fig)
        plt.close(fig)
        
        return {
            'type': 'histogram',
            'image': img_data,
            'format': 'png'
        }
    
    def export_chart(self, chart_type: str, data: np.ndarray, 
                    analysis: Dict[str, Any], config: Dict[str, Any], 
                    format: str) -> bytes:
        """Export chart in specified format.
        
        Args:
            chart_type: Type of chart to generate
            data: 2D numpy array with columns [time, voltage]
            analysis: Analysis results dictionary
            config: Chart configuration dictionary
            format: Export format ('png', 'svg', 'pdf')
            
        Returns:
            Bytes of the exported chart
        """
        # Update config for export
        export_config = config.copy()
        export_config['dpi'] = self._get_dpi(config)
        
        # Generate chart based on type
        if chart_type == 'waveform':
            chart_data = self._generate_waveform_figure(data, analysis, export_config)
        elif chart_type == 'ieee':
            chart_data = self._generate_ieee_figure(analysis, export_config)
        elif chart_type == 'fft':
            chart_data = self._generate_fft_figure(data, export_config)
        elif chart_type == 'histogram':
            chart_data = self._generate_histogram_figure(data, export_config)
        else:
            raise ValueError(f"Unknown chart type: {chart_type}")
        
        fig = chart_data['figure']
        
        # Export based on format
        output = io.BytesIO()
        
        if format == 'png':
            fig.savefig(output, format='png', dpi=export_config['dpi'], 
                       bbox_inches='tight', facecolor=self.colors['background'])
        elif format == 'svg':
            fig.savefig(output, format='svg', bbox_inches='tight', 
                       facecolor=self.colors['background'])
        elif format == 'pdf':
            fig.savefig(output, format='pdf', bbox_inches='tight', 
                       facecolor=self.colors['background'])
        
        plt.close(fig)
        output.seek(0)
        return output.read()
    
    def _apply_brutalist_style(self, fig, ax):
        """Apply brutalist styling to a matplotlib figure."""
        # Set background colors
        fig.patch.set_facecolor(self.colors['background'])
        ax.set_facecolor(self.colors['background'])
        
        # Configure spines (borders)
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
            spine.set_linewidth(1.5)
        
        # Remove top and right spines for cleaner look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Configure grid
        ax.grid(True, color=self.colors['grid'], linestyle='-', linewidth=0.5, alpha=0.5)
        ax.set_axisbelow(True)
        
        # Configure tick parameters
        ax.tick_params(colors=self.colors['text'], labelsize=10)
        
        # Set label colors
        ax.xaxis.label.set_color(self.colors['text'])
        ax.yaxis.label.set_color(self.colors['text'])
    
    def _normalize_voltage(self, voltage: np.ndarray) -> np.ndarray:
        """Normalize voltage values to 0-1 range."""
        v_min = np.min(voltage)
        v_max = np.max(voltage)
        if v_max - v_min > 0:
            return (voltage - v_min) / (v_max - v_min)
        return voltage
    
    def _get_figsize(self, config: Dict[str, Any]) -> Tuple[float, float]:
        """Get figure size from config or use defaults."""
        resolution_type = config.get('resolution_type', 'dpi')
        
        if resolution_type == 'pixels':
            # Convert pixels to inches using DPI
            dpi = config.get('export_dpi', 300)
            width_px = config.get('width_px', 1200)
            height_px = config.get('height_px', 800)
            width = width_px / dpi
            height = height_px / dpi
            return (width, height)
        else:
            # Use inches directly
            width = config.get('width', 10)
            height = config.get('height', 6)
            return (width, height)
    
    def _get_dpi(self, config: Dict[str, Any]) -> int:
        """Get DPI from config or use defaults."""
        return config.get('export_dpi', 300)
    
    def _add_metrics_overlay(self, ax, analysis: Dict[str, Any]):
        """Add metrics overlay to the plot."""
        # Validate that required fields exist
        required_fields = ['frequency', 'percent_flicker', 'flicker_index']
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing analysis fields: {missing_fields}")
        
        metrics_text = (
            f"Frequency: {analysis['frequency']} Hz\n"
            f"Percent Flicker: {analysis['percent_flicker']}%\n"
            f"Flicker Index: {analysis['flicker_index']}"
        )
        
        ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='left',
                bbox=dict(boxstyle='square,pad=0.5', facecolor=self.colors['background'],
                         edgecolor=self.colors['accent'], linewidth=1),
                fontsize=10, color=self.colors['text'])
    
    def _add_standards_overlay(self, ax, analysis: Dict[str, Any]):
        """Add standards compliance overlay to the plot."""
        # Validate that required fields exist
        required_fields = ['ieee_1789_2015', 'california_ja8_2019', 'well_standard_v2']
        missing_fields = [field for field in required_fields if field not in analysis]
        if missing_fields:
            raise ValueError(f"Missing analysis fields: {missing_fields}")
        
        # Color mapping for results
        color_map = {
            'No Risk': 'green',
            'Low Risk': 'orange',
            'High Risk': 'red',
            True: 'green',
            False: 'red'
        }
        
        ieee_color = color_map.get(analysis['ieee_1789_2015'], 'black')
        ca_color = color_map.get(analysis['california_ja8_2019'], 'black')
        well_color = color_map.get(analysis['well_standard_v2'], 'black')
        
        standards_text = (
            f"IEEE 1789-2015: {analysis['ieee_1789_2015']}\n"
            f"California JA8: {'Pass' if analysis['california_ja8_2019'] else 'Fail'}\n"
            f"WELL v2: {'Pass' if analysis['well_standard_v2'] else 'Fail'}"
        )
        
        ax.text(0.98, 0.02, standards_text, transform=ax.transAxes,
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='square,pad=0.5', facecolor=self.colors['background'],
                         edgecolor=self.colors['accent'], linewidth=1),
                fontsize=10, color=self.colors['text'])
    
    def _configure_legend(self, ax, config: Dict[str, Any]):
        """Configure legend based on config settings."""
        legend_items = config.get('legend_items', [])
        position = config.get('legend_position', 'upper right')
        
        # Map position strings to matplotlib locations
        position_map = {
            'top left': 'upper left',
            'top center': 'upper center',
            'top right': 'upper right',
            'middle left': 'center left',
            'middle right': 'center right',
            'bottom left': 'lower left',
            'bottom center': 'lower center',
            'bottom right': 'lower right'
        }
        
        loc = position_map.get(position, 'upper right')
        
        if legend_items:
            ax.legend(legend_items, loc=loc, fontsize=config.get('legend_size', 10))
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 encoded string."""
        output = io.BytesIO()
        fig.savefig(output, format='png', dpi=self.default_dpi, 
                   bbox_inches='tight', facecolor=self.colors['background'])
        output.seek(0)
        img_data = base64.b64encode(output.read()).decode('utf-8')
        return f"data:image/png;base64,{img_data}"
    
    def _generate_waveform_figure(self, data: np.ndarray, analysis: Dict[str, Any], 
                                 config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate waveform figure for export."""
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        self._apply_brutalist_style(fig, ax)
        
        # Plot waveform
        time_ms = data[:, 0] * 1000
        voltage_normalized = self._normalize_voltage(data[:, 1])
        ax.plot(time_ms, voltage_normalized, color=self.colors['data'], linewidth=2)
        
        # Configure axes and overlays
        ax.set_xlabel('Time (ms)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Light Output', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, time_ms[-1])
        ax.set_ylim(0, 1)
        
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        # Apply consistent font settings
        self._apply_font_settings(ax, config)
        
        # Add overlays if configured
        if config.get('show_metrics', True):
            self._add_metrics_overlay(ax, analysis)
        
        if config.get('show_standards', True):
            self._add_standards_overlay(ax, analysis)
        
        plt.tight_layout()
        return {'figure': fig}
    
    def _generate_ieee_figure(self, analysis: Dict[str, Any], 
                             config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate IEEE figure for export."""
        freq = analysis['frequency']
        pct_flicker = analysis['percent_flicker'] / 100
        name = config.get('data_label', 'Measurement')
        
        # Create the IEEE plot manually to have better control
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        
        # Set up the plot with IEEE specifications
        max_freq = 3000
        min_pct = 0.001
        
        ax.set_xlim([1, max_freq])
        ax.set_ylim([min_pct, 1])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Frequency (Hz)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Modulation (%)', fontsize=config.get('axis_label_size', 12))
        ax.grid(which='both', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Set custom tick labels for x-axis (1, 10, 100, 1000)
        x_ticks = [1, 10, 100, 1000]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(tick) for tick in x_ticks])
        
        # Set custom tick labels for y-axis (0.1%, 1%, 10%, 100%)
        y_ticks = [0.001, 0.01, 0.1, 1]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(['0.1%', '1%', '10%', '100%'])
        
        # Plot no risk region (green)
        norisk_region = [[1, min_pct], [1, 0.001], [10, 0.001], [100, 0.01], [100, 0.03], [3000, 1], 
                        [max_freq, 1], [max_freq, min_pct]]
        norisk = plt.Polygon(norisk_region, fc='green', alpha=0.3, label='No Risk')
        ax.add_patch(norisk)
        
        # Plot low risk region (yellow)
        lowrisk_region = [[1, 0.001], [1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], 
                         [3000, 1], [100, 0.03], [100, 0.025], [100, 0.01], [10, 0.001]]
        lowrisk = plt.Polygon(lowrisk_region, fc='yellow', alpha=0.3, label='Low Risk')
        ax.add_patch(lowrisk)
        
        # Plot high risk region (red)
        highrisk_region = [[1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], [1, 1]]
        highrisk = plt.Polygon(highrisk_region, fc='red', alpha=0.2, label='High Risk')
        ax.add_patch(highrisk)
        
        # Plot the data point
        ax.scatter(freq, pct_flicker, color=self.colors['data'], s=100, marker='o', 
                  label=name, alpha=1, edgecolors='black', linewidth=2, zorder=5)
        
        # Add legend
        ax.legend(loc='upper right', fontsize=config.get('legend_size', 10))
        
        # Add title if configured
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        # Apply brutalist styling
        self._apply_brutalist_style(fig, ax)
        
        plt.tight_layout()
        
        return {'figure': fig}
    
    def _generate_fft_figure(self, data: np.ndarray, 
                            config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate FFT figure for export."""
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        self._apply_brutalist_style(fig, ax)
        
        # Perform FFT analysis
        values = data[:, 1]
        time_diff = data[1, 0] - data[0, 0]
        framerate = int(1 / time_diff)
        
        values = values - np.mean(values)
        fft_values = np.fft.fft(values)
        fft_freq = np.fft.fftfreq(len(values), 1/framerate)
        
        positive_freq_idx = fft_freq > 0
        frequencies = fft_freq[positive_freq_idx]
        magnitudes = np.abs(fft_values[positive_freq_idx])
        magnitudes = magnitudes / np.max(magnitudes)
        
        freq_limit = min(3000, np.max(frequencies))
        relevant_idx = frequencies <= freq_limit
        
        ax.plot(frequencies[relevant_idx], magnitudes[relevant_idx], 
               color=self.colors['data'], linewidth=2)
        
        ax.set_xlabel('Frequency (Hz)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Magnitude (normalized)', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, freq_limit)
        ax.set_ylim(0, 1.1)
        
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        plt.tight_layout()
        return {'figure': fig}
    
    def _generate_histogram_figure(self, data: np.ndarray, 
                                  config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate histogram figure for export."""
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        self._apply_brutalist_style(fig, ax)
        
        voltage_normalized = self._normalize_voltage(data[:, 1])
        n_bins = config.get('n_bins', 50)
        
        ax.hist(voltage_normalized, bins=n_bins, color=self.colors['data'], 
                edgecolor=self.colors['accent'], alpha=0.8)
        
        ax.set_xlabel('Light Output', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Count', fontsize=config.get('axis_label_size', 12))
        ax.set_xlim(0, 1)
        
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        plt.tight_layout()
        return {'figure': fig}
    
    def _generate_ieee_plot_original(self, plot_data: List[Tuple[float, float, str]], 
                                   config: Dict[str, Any]) -> plt.Figure:
        """Generate IEEE plot with multiple data points using original styling.
        
        Args:
            plot_data: List of (frequency, modulation, label) tuples
            config: Chart configuration
            
        Returns:
            matplotlib Figure object
        """
        # Create the IEEE plot manually to have better control
        fig, ax = plt.subplots(figsize=self._get_figsize(config))
        
        # Set up the plot with IEEE specifications
        max_freq = 3000
        min_pct = 0.001
        
        ax.set_xlim([1, max_freq])
        ax.set_ylim([min_pct, 1])
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlabel('Frequency (Hz)', fontsize=config.get('axis_label_size', 12))
        ax.set_ylabel('Modulation (%)', fontsize=config.get('axis_label_size', 12))
        ax.grid(which='both', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Set custom tick labels for x-axis (1, 10, 100, 1000)
        x_ticks = [1, 10, 100, 1000]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(tick) for tick in x_ticks])
        
        # Set custom tick labels for y-axis (0.1%, 1%, 10%, 100%)
        y_ticks = [0.001, 0.01, 0.1, 1]
        ax.set_yticks(y_ticks)
        ax.set_yticklabels(['0.1%', '1%', '10%', '100%'])
        
        # Plot no risk region (green)
        norisk_region = [[1, min_pct], [1, 0.001], [10, 0.001], [100, 0.01], [100, 0.03], [3000, 1], 
                        [max_freq, 1], [max_freq, min_pct]]
        norisk = plt.Polygon(norisk_region, fc='green', alpha=0.3, label='No Risk')
        ax.add_patch(norisk)
        
        # Plot low risk region (yellow)
        lowrisk_region = [[1, 0.001], [1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], 
                         [3000, 1], [100, 0.03], [100, 0.025], [100, 0.01], [10, 0.001]]
        lowrisk = plt.Polygon(lowrisk_region, fc='yellow', alpha=0.3, label='Low Risk')
        ax.add_patch(lowrisk)
        
        # Plot high risk region (red)
        highrisk_region = [[1, 0.002], [8, 0.002], [90, 0.025], [90, 0.075], [1200, 1], [1, 1]]
        highrisk = plt.Polygon(highrisk_region, fc='red', alpha=0.2, label='High Risk')
        ax.add_patch(highrisk)
        
        # Plot all data points with distinct colors and markers
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Plot the actual data points
        for i, (freq, mod, label) in enumerate(plot_data):
            color = colors[i % len(colors)]
            
            # Use different markers for manual points vs data points
            if 'Manual:' in label:
                marker = 's'  # Square for manual points
                marker_size = 120
                edge_width = 2
                alpha = 0.9
            else:
                marker = 'o'  # Circle for data points
                marker_size = 100
                edge_width = 2
                alpha = 1.0
            
            # Plot the point
            ax.scatter(freq, mod, color=color, s=marker_size, marker=marker, 
                      alpha=alpha, edgecolors='black', linewidth=edge_width, zorder=5)
        
        # Add comprehensive legend
        legend_elements = []
        
        # Add risk region legend
        legend_elements.extend([
            plt.Rectangle((0, 0), 1, 1, facecolor='lightgreen', alpha=0.3, label='No Risk'),
            plt.Rectangle((0, 0), 1, 1, facecolor='yellow', alpha=0.3, label='Low Risk'),
            plt.Rectangle((0, 0), 1, 1, facecolor='lightcoral', alpha=0.3, label='High Risk')
        ])
        
        # Add data point legends
        for i, (freq, mod, label) in enumerate(plot_data):
            color = colors[i % len(colors)]
            marker = 's' if 'Manual:' in label else 'o'
            legend_elements.append(plt.Line2D([0], [0], marker=marker, color='w', 
                                            markerfacecolor=color, markersize=8, 
                                            label=f'{label}: {freq:.1f} Hz, {mod*100:.1f}%'))
        
        # Get legend position from config, default to upper left
        legend_position = config.get('legend_position', 'upper left')
        
        ax.legend(handles=legend_elements, loc=legend_position, 
                 fontsize=config.get('legend_size', 10), framealpha=0.9)
        
        # Add title if configured
        title = config.get('title', 'IEEE PAR 1789-2015 Flicker Compliance')
        ax.set_title(title, fontsize=config.get('title_size', 16), 
                    fontweight='bold', pad=20)
        
        # Apply brutalist styling
        self._apply_brutalist_style(fig, ax)
        
        # Adjust layout to accommodate legend
        plt.tight_layout()
        
        return fig
    
    def _apply_font_settings(self, ax, config: Dict[str, Any]):
        """Apply consistent font settings to chart elements."""
        font_family = config.get('font', 'Inter')
        title_size = config.get('title_size', 16)
        axis_size = config.get('axis_label_size', 12)
        
        # Set title font to match axis labels font family
        if config.get('title'):
            ax.set_title(config['title'], fontsize=title_size, 
                        fontfamily=font_family, fontweight='normal', pad=20)
        
        # Set axis label fonts
        ax.set_xlabel(ax.get_xlabel(), fontsize=axis_size, fontfamily=font_family)
        ax.set_ylabel(ax.get_ylabel(), fontsize=axis_size, fontfamily=font_family)
        
        # Set tick label fonts
        ax.tick_params(labelsize=axis_size-2)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontfamily(font_family)