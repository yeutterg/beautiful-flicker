"""Test that all modules can be imported."""

try:
    print("Testing module imports...")
    
    # Test data processing
    from data_processing import CSVProcessor
    print("✓ CSVProcessor imported")
    
    # Test flicker analysis  
    from flicker_analysis import FlickerAnalyzer
    print("✓ FlickerAnalyzer imported")
    
    # Test visualization
    from visualization import ChartGenerator
    print("✓ ChartGenerator imported")
    
    print("\n✅ All modules imported successfully!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")