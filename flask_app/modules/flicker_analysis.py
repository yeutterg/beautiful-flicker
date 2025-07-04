"""Flicker analysis module for Beautiful Flicker Flask app."""

import sys
import os
import numpy as np
from typing import Dict, Any, Tuple

# Import from the src directory (copied to /app/src/ in Docker)
from src.waveform import Waveform, frequency, percent_flicker, flicker_index
from src.standards import ieee_1789_2015, california_ja8_2019, well_building_standard_v2


class FlickerAnalyzer:
    """Handles flicker analysis operations."""
    
    def analyze(self, data: np.ndarray) -> Dict[str, Any]:
        """Perform basic flicker analysis on waveform data.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract basic parameters
            v_max = data[:, 1].max()
            v_min = data[:, 1].min()
            v_pp = v_max - v_min
            v_avg = np.mean([v_max, v_min])
            
            # Calculate framerate
            time_diff = data[1, 0] - data[0, 0]
            framerate_val = int(1 / time_diff)
            
            # Calculate frequency
            freq = frequency(data, framerate_val, v_avg)
            
            # Calculate flicker metrics
            pct_flicker = percent_flicker(v_max, v_pp)
            flicker_idx = self._calculate_flicker_index(data, v_avg, freq)
            
            # Check standards compliance
            ieee_result = ieee_1789_2015(freq, pct_flicker)
            ca_ja8_result = california_ja8_2019(freq, pct_flicker)
            well_result = well_building_standard_v2(freq, pct_flicker)
            
            return {
                'v_max': round(v_max, 3),
                'v_min': round(v_min, 3),
                'v_pp': round(v_pp, 3),
                'v_avg': round(v_avg, 3),
                'frequency': round(freq, 1),
                'percent_flicker': round(pct_flicker, 1),
                'flicker_index': round(flicker_idx, 3),
                'ieee_1789_2015': ieee_result,
                'california_ja8_2019': ca_ja8_result,
                'well_standard_v2': well_result,
                'framerate': framerate_val
            }
            
        except Exception as e:
            raise ValueError(f"Error analyzing waveform: {str(e)}")
    
    def comprehensive_analysis(self, data: np.ndarray) -> Dict[str, Any]:
        """Perform comprehensive flicker analysis including FFT.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        # Get basic analysis
        basic_analysis = self.analyze(data)
        
        # Add FFT analysis
        fft_results = self._perform_fft_analysis(data, basic_analysis['framerate'])
        
        # Add RMS variation
        rms_variation = self._calculate_rms_variation(data[:, 1])
        
        return {
            **basic_analysis,
            'fft_dominant_frequency': fft_results['dominant_frequency'],
            'fft_frequencies': fft_results['frequencies'].tolist(),
            'fft_magnitudes': fft_results['magnitudes'].tolist(),
            'rms_variation': round(rms_variation, 3)
        }
    
    def _calculate_flicker_index(self, data: np.ndarray, v_avg: float, freq: float) -> float:
        """Calculate flicker index for one period of the waveform."""
        try:
            # Get one period of data
            period = 1 / freq
            time_per_sample = data[1, 0] - data[0, 0]
            samples_per_period = int(period / time_per_sample)
            
            # Extract one period starting from a rising edge crossing v_avg
            start_idx = self._find_rising_edge(data[:, 1], v_avg)
            end_idx = min(start_idx + samples_per_period, len(data))
            one_period_data = data[start_idx:end_idx]
            
            # Calculate areas above and below average
            values = one_period_data[:, 1]
            above_avg = values[values > v_avg] - v_avg
            below_avg = v_avg - values[values < v_avg]
            
            area_above = np.sum(above_avg)
            area_below = np.sum(below_avg)
            total_area = area_above + area_below
            
            if total_area > 0:
                return (area_above - area_below) / total_area
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _find_rising_edge(self, values: np.ndarray, threshold: float) -> int:
        """Find the index of the first rising edge crossing the threshold."""
        for i in range(1, len(values)):
            if values[i-1] <= threshold < values[i]:
                return i
        return 0
    
    def _perform_fft_analysis(self, data: np.ndarray, framerate: int) -> Dict[str, Any]:
        """Perform FFT analysis on the waveform."""
        values = data[:, 1]
        
        # Remove DC component
        values = values - np.mean(values)
        
        # Perform FFT
        fft_values = np.fft.fft(values)
        fft_freq = np.fft.fftfreq(len(values), 1/framerate)
        
        # Get positive frequencies only
        positive_freq_idx = fft_freq > 0
        frequencies = fft_freq[positive_freq_idx]
        magnitudes = np.abs(fft_values[positive_freq_idx])
        
        # Normalize magnitudes
        magnitudes = magnitudes / np.max(magnitudes)
        
        # Find dominant frequency
        dominant_idx = np.argmax(magnitudes)
        dominant_frequency = frequencies[dominant_idx]
        
        # Limit to relevant frequency range (0-3000 Hz)
        relevant_idx = frequencies <= 3000
        frequencies = frequencies[relevant_idx]
        magnitudes = magnitudes[relevant_idx]
        
        return {
            'frequencies': frequencies,
            'magnitudes': magnitudes,
            'dominant_frequency': round(dominant_frequency, 1)
        }
    
    def _calculate_rms_variation(self, values: np.ndarray) -> float:
        """Calculate RMS variation of the signal."""
        mean_val = np.mean(values)
        if mean_val == 0:
            return 0.0
        
        rms = np.sqrt(np.mean((values - mean_val) ** 2))
        return (rms / mean_val) * 100