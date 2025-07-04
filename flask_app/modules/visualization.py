"""Visualization module for Beautiful Flicker Flask app."""

import sys
import os
import io
import base64
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_svg_renderer import FigureCanvasSVG
from matplotlib.backends.backend_pdf import PdfPages
from typing import Dict, Any, Optional, Tuple

# Add the src directory to the path to import existing modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..', 'src'))

from plot import ieee_par_1789_graph


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
        
        # Add title if configured
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
        # Add metrics overlay if enabled
        if config.get('show_metrics', True):
            self._add_metrics_overlay(ax, analysis)
        
        # Add standards overlay if enabled
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
        # Prepare data for IEEE plot
        freq = analysis['frequency']
        pct_flicker = analysis['percent_flicker'] / 100  # Convert to decimal
        name = config.get('title', 'Measurement')
        
        data_points = [(freq, pct_flicker, name)]
        
        # Create figure
        fig = plt.figure(figsize=self._get_figsize(config))
        
        # Generate IEEE plot using existing function
        ieee_par_1789_graph(
            data_points, 
            figsize=self._get_figsize(config),
            showred=True,
            showyellow=True,
            noriskcolor=True,
            suppress=True
        )
        
        # Apply brutalist styling to current figure
        ax = plt.gca()
        self._apply_brutalist_style(fig, ax)
        
        # Convert to base64
        img_data = self._fig_to_base64(fig)
        plt.close(fig)
        
        return {
            'type': 'ieee',
            'image': img_data,
            'format': 'png'
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
        export_config['dpi'] = config.get('export_dpi', 300)
        
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
        """Get figure size from config or use default."""
        width = config.get('fig_width', self.default_figsize[0])
        height = config.get('fig_height', self.default_figsize[1])
        return (width, height)
    
    def _add_metrics_overlay(self, ax, analysis: Dict[str, Any]):
        """Add metrics overlay to the plot."""
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
        
        if config.get('title'):
            ax.set_title(config['title'], fontsize=config.get('title_size', 16), 
                        fontweight='bold', pad=20)
        
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
        name = config.get('title', 'Measurement')
        
        fig = plt.figure(figsize=self._get_figsize(config))
        
        ieee_par_1789_graph(
            [(freq, pct_flicker, name)], 
            figsize=self._get_figsize(config),
            showred=True,
            showyellow=True,
            noriskcolor=True,
            suppress=True
        )
        
        ax = plt.gca()
        self._apply_brutalist_style(fig, ax)
        
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