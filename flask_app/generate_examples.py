"""Generate example CSV files for Beautiful Flicker Flask app."""

import os
import sys
import numpy as np

# Add modules to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from data_processing import CSVProcessor

def main():
    """Generate example CSV files."""
    processor = CSVProcessor()
    
    # Ensure examples directory exists
    examples_dir = os.path.join(os.path.dirname(__file__), 'data', 'examples')
    os.makedirs(examples_dir, exist_ok=True)
    
    # Generate 60Hz incandescent example
    print("Generating 60Hz incandescent example...")
    data_60hz = processor.generate_example_data(frequency=60.0, percent_flicker=5.0)
    np.savetxt(
        os.path.join(examples_dir, '60hz_incandescent.csv'), 
        data_60hz, 
        delimiter=',', 
        header='Time,Value', 
        comments=''
    )
    
    # Generate LED PWM dimming example
    print("Generating LED PWM dimming example...")
    data_led = processor.generate_example_data(frequency=1000.0, percent_flicker=20.0, duration=0.01)
    np.savetxt(
        os.path.join(examples_dir, 'led_pwm_dimming.csv'), 
        data_led, 
        delimiter=',', 
        header='Time,Value', 
        comments=''
    )
    
    # Generate fluorescent magnetic ballast example
    print("Generating fluorescent magnetic ballast example...")
    data_fluor = processor.generate_example_data(frequency=120.0, percent_flicker=30.0)
    np.savetxt(
        os.path.join(examples_dir, 'fluorescent_magnetic.csv'), 
        data_fluor, 
        delimiter=',', 
        header='Time,Value', 
        comments=''
    )
    
    print("Example files created successfully!")

if __name__ == '__main__':
    main()