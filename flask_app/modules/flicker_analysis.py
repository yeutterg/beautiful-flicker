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
        """Detect fundamental flicker frequency using improved signal processing.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            framerate: Sample rate in Hz
            
        Returns:
            Detected fundamental frequency in Hz
        """
        try:
            values = data[:, 1]
            
            # Step 1: Preprocessing and cleaning
            cleaned_values = self._preprocess_signal(values)
            
            # Step 2: Multiple detection methods focusing on fundamental frequency
            fft_freq = self._improved_fft_fundamental_detection(cleaned_values, framerate)
            autocorr_freq = self._improved_autocorrelation_detection(cleaned_values, framerate)
            zero_cross_freq = self._improved_zero_crossing_detection(cleaned_values, framerate)
            
            # Step 3: Harmonic analysis to find true fundamental
            candidates = [f for f in [fft_freq, autocorr_freq, zero_cross_freq] if f is not None]
            
            if not candidates:
                return 120.0  # Default fallback
            
            # Find the fundamental frequency among candidates
            fundamental_freq = self._find_fundamental_frequency(candidates)
            
            print(f"Frequency detection - FFT: {fft_freq}, Autocorr: {autocorr_freq}, ZeroCross: {zero_cross_freq}, Final: {fundamental_freq}")
            
            return fundamental_freq
            
        except Exception as e:
            print(f"Frequency detection error: {e}")
            return 120.0  # Default fallback
    
    def _preprocess_signal(self, values: np.ndarray) -> np.ndarray:
        """Preprocess signal to remove noise and outliers."""
        try:
            from scipy.signal import savgol_filter, medfilt
            
            # Remove outliers using median filter
            values_filtered = medfilt(values, kernel_size=5)
            
            # Remove DC component
            values_centered = values_filtered - np.mean(values_filtered)
            
            # Apply Savitzky-Golay filter for smoothing while preserving peaks
            if len(values_centered) > 50:
                window_length = min(51, len(values_centered) // 10)
                if window_length % 2 == 0:
                    window_length += 1
                values_smooth = savgol_filter(values_centered, window_length, 3)
            else:
                values_smooth = values_centered
            
            # Normalize to unit variance
            std_val = np.std(values_smooth)
            if std_val > 0:
                values_smooth = values_smooth / std_val
            
            return values_smooth
            
        except Exception:
            # Fallback to simple preprocessing
            values_centered = values - np.mean(values)
            std_val = np.std(values_centered)
            if std_val > 0:
                values_centered = values_centered / std_val
            return values_centered
    
    def _improved_fft_fundamental_detection(self, values: np.ndarray, framerate: int) -> float:
        """Detect fundamental frequency using improved FFT analysis."""
        try:
            # Apply window function to reduce spectral leakage
            window = np.hanning(len(values))
            values_windowed = values * window
            
            # Zero-padding for better frequency resolution
            n_fft = max(2048, 2**int(np.ceil(np.log2(len(values)))))
            
            # Perform FFT
            fft_vals = np.fft.fft(values_windowed, n_fft)
            fft_freqs = np.fft.fftfreq(n_fft, 1/framerate)
            
            # Get positive frequencies only
            positive_mask = fft_freqs > 0
            freqs = fft_freqs[positive_mask]
            magnitudes = np.abs(fft_vals[positive_mask])
            
            # Focus on lighting frequency range (10-1000 Hz)
            freq_mask = (freqs >= 10) & (freqs <= 1000)
            freqs = freqs[freq_mask]
            magnitudes = magnitudes[freq_mask]
            
            if len(freqs) == 0:
                return None
            
            # Find peaks in the spectrum
            from scipy.signal import find_peaks
            
            # Normalize magnitudes
            magnitudes_norm = magnitudes / np.max(magnitudes)
            
            # Find significant peaks (at least 10% of maximum)
            peaks, properties = find_peaks(magnitudes_norm, height=0.1, distance=int(framerate/1000))
            
            if len(peaks) == 0:
                # Fallback to simple peak finding
                peak_idx = np.argmax(magnitudes_norm)
                return float(freqs[peak_idx])
            
            # Get peak frequencies and their magnitudes
            peak_freqs = freqs[peaks]
            peak_mags = magnitudes_norm[peaks]
            
            # Sort by magnitude (strongest first)
            sorted_indices = np.argsort(peak_mags)[::-1]
            peak_freqs_sorted = peak_freqs[sorted_indices]
            
            # Look for fundamental frequency (lowest frequency that explains other peaks as harmonics)
            for candidate_fundamental in peak_freqs_sorted:
                if self._is_likely_fundamental(candidate_fundamental, peak_freqs_sorted):
                    return float(candidate_fundamental)
            
            # If no clear fundamental found, return the strongest peak
            return float(peak_freqs_sorted[0])
            
        except Exception:
            return None
    
    def _improved_autocorrelation_detection(self, values: np.ndarray, framerate: int) -> float:
        """Improved autocorrelation-based frequency detection."""
        try:
            # Calculate normalized autocorrelation
            values_norm = values - np.mean(values)
            autocorr = np.correlate(values_norm, values_norm, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Normalize autocorrelation
            if autocorr[0] != 0:
                autocorr = autocorr / autocorr[0]
            
            # Define search range for lighting frequencies
            min_period_samples = int(framerate / 1000)  # Max 1000 Hz
            max_period_samples = int(framerate / 10)    # Min 10 Hz
            
            if max_period_samples >= len(autocorr):
                max_period_samples = len(autocorr) - 1
            
            # Find peaks in autocorrelation
            search_range = autocorr[min_period_samples:max_period_samples]
            
            if len(search_range) == 0:
                return None
            
            from scipy.signal import find_peaks
            
            # Find significant peaks
            peaks, _ = find_peaks(search_range, height=0.1, distance=min_period_samples//2)
            
            if len(peaks) == 0:
                # Fallback to maximum
                peak_idx = np.argmax(search_range)
                period_samples = peak_idx + min_period_samples
            else:
                # Take the first significant peak (shortest period = highest frequency)
                peak_idx = peaks[0]
                period_samples = peak_idx + min_period_samples
            
            frequency = framerate / period_samples
            
            # Validate frequency range
            if 10 <= frequency <= 1000:
                return float(frequency)
            
            return None
            
        except Exception:
            return None
    
    def _improved_zero_crossing_detection(self, values: np.ndarray, framerate: int) -> float:
        """Improved zero-crossing frequency detection."""
        try:
            # Find zero crossings
            zero_crossings = np.where(np.diff(np.sign(values)))[0]
            
            if len(zero_crossings) < 4:  # Need at least 2 full cycles
                return None
            
            # Calculate intervals between zero crossings
            crossing_intervals = np.diff(zero_crossings)
            
            # Remove outliers (intervals that are too different from median)
            median_interval = np.median(crossing_intervals)
            valid_intervals = crossing_intervals[
                np.abs(crossing_intervals - median_interval) < 2 * np.std(crossing_intervals)
            ]
            
            if len(valid_intervals) == 0:
                return None
            
            # Calculate frequency from average half-period
            avg_half_period = np.mean(valid_intervals)
            frequency = framerate / (2 * avg_half_period)
            
            # Validate frequency range
            if 10 <= frequency <= 1000:
                return float(frequency)
            
            return None
            
        except Exception:
            return None
    
    def _is_likely_fundamental(self, candidate: float, all_peaks: np.ndarray) -> bool:
        """Check if a candidate frequency is likely the fundamental frequency."""
        try:
            # Check if other peaks are harmonics of this candidate
            harmonics_found = 0
            expected_harmonics = [2, 3, 4, 5]  # Check first few harmonics
            
            for harmonic in expected_harmonics:
                expected_freq = candidate * harmonic
                # Look for peaks within 5% of expected harmonic frequency
                tolerance = expected_freq * 0.05
                harmonic_present = np.any(np.abs(all_peaks - expected_freq) < tolerance)
                if harmonic_present:
                    harmonics_found += 1
            
            # If we find at least one harmonic, this is likely the fundamental
            return harmonics_found >= 1
            
        except Exception:
            return True  # Default to accepting the candidate
    
    def _find_fundamental_frequency(self, candidates: list) -> float:
        """Find the fundamental frequency from a list of candidates."""
        try:
            if len(candidates) == 1:
                return candidates[0]
            
            # Remove obvious harmonics
            candidates_sorted = sorted(candidates)
            fundamental_candidates = []
            
            for freq in candidates_sorted:
                # Check if this frequency is a harmonic of any lower frequency
                is_harmonic = False
                for lower_freq in fundamental_candidates:
                    # Check if freq is approximately 2x, 3x, 4x, etc. of lower_freq
                    for harmonic in [2, 3, 4, 5, 6]:
                        expected = lower_freq * harmonic
                        if abs(freq - expected) / expected < 0.1:  # Within 10%
                            is_harmonic = True
                            break
                    if is_harmonic:
                        break
                
                if not is_harmonic:
                    fundamental_candidates.append(freq)
            
            if fundamental_candidates:
                # Return the lowest frequency that's not a harmonic
                return min(fundamental_candidates)
            else:
                # Fallback to lowest frequency
                return min(candidates)
                
        except Exception:
            return min(candidates) if candidates else 120.0