"""Data processing module for Beautiful Flicker Flask app."""

import io
import csv
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional


class CSVProcessor:
    """Handles CSV file processing and validation."""
    
    def __init__(self):
        """Initialize the CSV processor."""
        self.allowed_extensions = {'csv', 'txt'}
        self.required_columns = ['time', 'voltage', 'value', 'light']  # Various possible column names
    
    def allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if file extension is allowed, False otherwise
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def process_csv_content(self, content: str) -> np.ndarray:
        """Process CSV content and convert to numpy array.
        
        Args:
            content: CSV file content as string
            
        Returns:
            2D numpy array with columns [time, voltage]
            
        Raises:
            ValueError: If CSV format is invalid or required columns are missing
        """
        try:
            # Try to read CSV with pandas for better handling of different formats
            df = pd.read_csv(io.StringIO(content))
            
            # Clean column names (remove whitespace, convert to lowercase)
            df.columns = df.columns.str.strip().str.lower()
            
            # Find time and value columns
            time_col = self._find_column(df, ['time', 't', 'x', 'seconds', 's'])
            value_col = self._find_column(df, ['voltage', 'value', 'light', 'y', 'v', 'intensity'])
            
            if time_col is None or value_col is None:
                # Try to infer from first two columns if specific names not found
                if len(df.columns) >= 2:
                    time_col = df.columns[0]
                    value_col = df.columns[1]
                else:
                    raise ValueError("Could not identify time and value columns")
            
            # Extract data
            time_data = pd.to_numeric(df[time_col], errors='coerce')
            value_data = pd.to_numeric(df[value_col], errors='coerce')
            
            # Remove NaN values
            valid_mask = ~(time_data.isna() | value_data.isna())
            time_data = time_data[valid_mask].values
            value_data = value_data[valid_mask].values
            
            if len(time_data) < 10:
                raise ValueError("Insufficient valid data points (minimum 10 required)")
            
            # Create numpy array
            data = np.column_stack((time_data, value_data))
            
            # Sort by time
            data = data[data[:, 0].argsort()]
            
            # Validate data
            self._validate_data(data)
            
            return data
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except Exception as e:
            raise ValueError(f"Error processing CSV: {str(e)}")
    
    def get_preview(self, data: np.ndarray, max_rows: int = 10) -> Dict[str, Any]:
        """Get a preview of the processed data.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            max_rows: Maximum number of rows to include in preview
            
        Returns:
            Dictionary containing preview information
        """
        num_rows = min(len(data), max_rows)
        
        return {
            'total_rows': len(data),
            'preview_rows': num_rows,
            'columns': ['Time (s)', 'Value'],
            'data': [
                {
                    'time': round(float(data[i, 0]), 6),
                    'value': round(float(data[i, 1]), 6)
                }
                for i in range(num_rows)
            ],
            'time_range': {
                'min': round(float(data[:, 0].min()), 6),
                'max': round(float(data[:, 0].max()), 6),
                'duration': round(float(data[:, 0].max() - data[:, 0].min()), 6)
            },
            'value_range': {
                'min': round(float(data[:, 1].min()), 6),
                'max': round(float(data[:, 1].max()), 6)
            }
        }
    
    def _find_column(self, df: pd.DataFrame, possible_names: List[str]) -> Optional[str]:
        """Find a column by trying multiple possible names.
        
        Args:
            df: Pandas DataFrame
            possible_names: List of possible column names to search for
            
        Returns:
            Column name if found, None otherwise
        """
        for name in possible_names:
            if name in df.columns:
                return name
            # Also try partial matches
            for col in df.columns:
                if name in col:
                    return col
        return None
    
    def _validate_data(self, data: np.ndarray) -> None:
        """Validate the processed data.
        
        Args:
            data: 2D numpy array with columns [time, voltage]
            
        Raises:
            ValueError: If data is invalid
        """
        if data.shape[0] < 10:
            raise ValueError("Insufficient data points (minimum 10 required)")
        
        if data.shape[1] != 2:
            raise ValueError("Data must have exactly 2 columns (time and value)")
        
        # Check for non-finite values
        if not np.all(np.isfinite(data)):
            raise ValueError("Data contains non-finite values (inf or nan)")
        
        # Check time is monotonically increasing
        time_diff = np.diff(data[:, 0])
        if np.any(time_diff <= 0):
            raise ValueError("Time values must be monotonically increasing")
        
        # Check for reasonable sample rate
        avg_time_diff = np.mean(time_diff)
        if avg_time_diff <= 0 or avg_time_diff > 1:
            raise ValueError("Unreasonable sample rate detected")
    
    def generate_example_data(self, frequency: float = 120.0, 
                            duration: float = 0.1,
                            sample_rate: int = 10000,
                            percent_flicker: float = 10.0) -> np.ndarray:
        """Generate example flicker waveform data.
        
        Args:
            frequency: Flicker frequency in Hz
            duration: Duration in seconds
            sample_rate: Samples per second
            percent_flicker: Percent flicker
            
        Returns:
            2D numpy array with columns [time, voltage]
        """
        # Generate time array
        num_samples = int(duration * sample_rate)
        time = np.linspace(0, duration, num_samples)
        
        # Generate flicker waveform
        # Base signal with flicker
        amplitude = 1.0
        flicker_amplitude = amplitude * (percent_flicker / 100)
        
        # Create waveform with flicker at specified frequency
        base_signal = amplitude
        flicker_signal = flicker_amplitude * np.sin(2 * np.pi * frequency * time)
        voltage = base_signal + flicker_signal
        
        # Add some noise for realism
        noise = np.random.normal(0, 0.001, num_samples)
        voltage += noise
        
        # Ensure voltage stays positive
        voltage = np.maximum(voltage, 0)
        
        return np.column_stack((time, voltage))