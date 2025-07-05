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
            
            # Calculate frequency using improved method
            freq = self._detect_flicker_frequency(data, framerate_val)
            
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
    
    def _detect_flicker_frequency(self, data: np.ndarray, framerate: int) -> float:
        """Detect flicker frequency using multiple methods for robustness.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            framerate: Sample rate in Hz
            
        Returns:
            Detected frequency in Hz
        """
        try:
            values = data[:, 1]
            
            # Method 1: FFT-based frequency detection
            fft_freq = self._fft_frequency_detection(values, framerate)
            
            # Method 2: Autocorrelation-based detection
            autocorr_freq = self._autocorrelation_frequency_detection(values, framerate)
            
            # Method 3: Envelope detection for high sample rate data
            envelope_freq = self._envelope_frequency_detection(values, framerate)
            
            # Choose the best frequency based on consistency and expected ranges
            candidates = [fft_freq, autocorr_freq, envelope_freq]
            candidates = [f for f in candidates if f is not None and 10 <= f <= 2000]
            
            if not candidates:
                # Fallback to zero-crossing method
                return self._zero_crossing_frequency(values, framerate)
            
            # Return the median of valid candidates (more robust than mean)
            return np.median(candidates)
            
        except Exception as e:
            print(f"Frequency detection error: {e}")
            # Fallback to zero-crossing method
            return self._zero_crossing_frequency(values, framerate)
    
    def _fft_frequency_detection(self, values: np.ndarray, framerate: int) -> float:
        """Detect frequency using FFT analysis."""
        try:
            # Remove DC component and apply window
            values_centered = values - np.mean(values)
            
            # Apply Hanning window to reduce spectral leakage
            window = np.hanning(len(values_centered))
            values_windowed = values_centered * window
            
            # Perform FFT
            fft_vals = np.fft.fft(values_windowed)
            fft_freqs = np.fft.fftfreq(len(values_windowed), 1/framerate)
            
            # Get positive frequencies only
            positive_mask = fft_freqs > 0
            freqs = fft_freqs[positive_mask]
            magnitudes = np.abs(fft_vals[positive_mask])
            
            # Focus on lighting frequency range (10-2000 Hz)
            freq_mask = (freqs >= 10) & (freqs <= 2000)
            freqs = freqs[freq_mask]
            magnitudes = magnitudes[freq_mask]
            
            if len(freqs) == 0:
                return None
            
            # Find peak frequency
            peak_idx = np.argmax(magnitudes)
            peak_freq = freqs[peak_idx]
            
            # Validate that it's a significant peak
            if magnitudes[peak_idx] > 0.1 * np.max(magnitudes):
                return float(peak_freq)
            
            return None
            
        except Exception:
            return None
    
    def _autocorrelation_frequency_detection(self, values: np.ndarray, framerate: int) -> float:
        """Detect frequency using autocorrelation."""
        try:
            # Remove DC component
            values_centered = values - np.mean(values)
            
            # Calculate autocorrelation
            autocorr = np.correlate(values_centered, values_centered, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation (excluding the zero-lag peak)
            min_period_samples = int(framerate / 2000)  # Max 2000 Hz
            max_period_samples = int(framerate / 10)    # Min 10 Hz
            
            if max_period_samples >= len(autocorr):
                return None
            
            # Look for the first significant peak after the minimum period
            search_range = autocorr[min_period_samples:max_period_samples]
            if len(search_range) == 0:
                return None
            
            # Find local maxima
            peaks = []
            for i in range(1, len(search_range) - 1):
                if search_range[i] > search_range[i-1] and search_range[i] > search_range[i+1]:
                    if search_range[i] > 0.1 * np.max(search_range):
                        peaks.append(i + min_period_samples)
            
            if peaks:
                # Take the first significant peak
                period_samples = peaks[0]
                frequency = framerate / period_samples
                return float(frequency)
            
            return None
            
        except Exception:
            return None
    
    def _envelope_frequency_detection(self, values: np.ndarray, framerate: int) -> float:
        """Detect frequency using envelope detection (useful for high sample rates)."""
        try:
            from scipy.signal import hilbert, find_peaks
            
            # Remove DC component
            values_centered = values - np.mean(values)
            
            # Get envelope using Hilbert transform
            analytic_signal = hilbert(values_centered)
            envelope = np.abs(analytic_signal)
            
            # Remove trend from envelope
            envelope_detrended = envelope - np.mean(envelope)
            
            # Find peaks in envelope
            peaks, _ = find_peaks(envelope_detrended, height=0.1*np.std(envelope_detrended))
            
            if len(peaks) < 2:
                return None
            
            # Calculate average period from peak spacing
            peak_intervals = np.diff(peaks)
            if len(peak_intervals) == 0:
                return None
            
            avg_period_samples = np.median(peak_intervals)
            frequency = framerate / avg_period_samples
            
            # Validate frequency range
            if 10 <= frequency <= 2000:
                return float(frequency)
            
            return None
            
        except Exception:
            return None
    
    def _zero_crossing_frequency(self, values: np.ndarray, framerate: int) -> float:
        """Fallback zero-crossing frequency detection (improved version)."""
        try:
            # Remove DC component
            v_avg = np.mean(values)
            values_centered = values - v_avg
            
            # Find zero crossings
            zero_crossings = np.where(np.diff(np.sign(values_centered)))[0]
            
            if len(zero_crossings) < 2:
                return 120.0  # Default fallback
            
            # Calculate frequency from zero crossings
            crossing_intervals = np.diff(zero_crossings)
            avg_half_period = np.median(crossing_intervals)
            frequency = framerate / (2 * avg_half_period)
            
            # Validate and return
            if 10 <= frequency <= 2000:
                return float(frequency)
            else:
                return 120.0  # Default fallback
                
        except Exception:
            return 120.0  # Default fallback