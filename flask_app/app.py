"""Beautiful Flicker Flask Web Application

A modern web interface for lighting flicker data analysis and visualization.
"""

import os
import io
import base64
import json
import uuid
import argparse
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from flask_app.modules.flicker_analysis import FlickerAnalyzer
from flask_app.modules.visualization import ChartGenerator
from flask_app.modules.data_processing import CSVProcessor

app = Flask(__name__)
app.config.from_object('flask_app.config.Config')
CORS(app)

# Initialize components
csv_processor = CSVProcessor()
flicker_analyzer = FlickerAnalyzer()
chart_generator = ChartGenerator()

# Store session data (in production, use Redis or similar)
session_data = {}

@app.route('/')
def index():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and CSV data processing."""
    try:
        session_id = str(uuid.uuid4())
        
        if 'file' in request.files:
            file = request.files['file']
            if file and csv_processor.allowed_file(file.filename):
                # Read and process CSV file
                file_content = file.read().decode('utf-8')
                data = csv_processor.process_csv_content(file_content)
                
                # Store in session
                session_data[session_id] = {
                    'raw_data': data,
                    'filename': secure_filename(file.filename)
                }
                
                # Perform initial analysis
                analysis = flicker_analyzer.analyze(data)
                
                # Store analysis in session
                session_data[session_id]['analysis'] = analysis
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'preview': csv_processor.get_preview(data),
                    'analysis': analysis
                })
        
        elif 'csv_data' in request.json:
            # Handle pasted CSV data
            csv_content = request.json['csv_data']
            data = csv_processor.process_csv_content(csv_content)
            
            # Store in session
            session_data[session_id] = {
                'raw_data': data,
                'filename': 'pasted_data.csv'
            }
            
            # Perform initial analysis
            analysis = flicker_analyzer.analyze(data)
            
            # Store analysis in session
            session_data[session_id]['analysis'] = analysis
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'preview': csv_processor.get_preview(data),
                'analysis': analysis
            })
            
        return jsonify({'success': False, 'error': 'No valid data provided'}), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Perform detailed flicker analysis on uploaded data."""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in session_data:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        data = session_data[session_id]['raw_data']
        
        # Perform comprehensive analysis
        analysis = flicker_analyzer.comprehensive_analysis(data)
        
        # Store analysis results
        session_data[session_id]['analysis'] = analysis
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/configure', methods=['POST'])
def configure_chart():
    """Update chart configuration."""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in session_data:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        config = request.json.get('config', {})
        
        # Store configuration
        session_data[session_id]['chart_config'] = config
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/chart/<chart_type>', methods=['POST'])
def generate_chart(chart_type):
    """Generate a specific type of chart."""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in session_data:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        data = session_data[session_id]['raw_data']
        analysis = session_data[session_id].get('analysis', {})
        config = session_data[session_id].get('chart_config', {})
        
        # Generate chart based on type
        if chart_type == 'waveform':
            chart_data = chart_generator.generate_waveform(data, analysis, config)
        elif chart_type == 'ieee':
            chart_data = chart_generator.generate_ieee_plot(analysis, config)
        elif chart_type == 'fft':
            chart_data = chart_generator.generate_fft_spectrum(data, config)
        elif chart_type == 'histogram':
            chart_data = chart_generator.generate_histogram(data, config)
        else:
            return jsonify({'success': False, 'error': 'Invalid chart type'}), 400
        
        return jsonify({
            'success': True,
            'chart': chart_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/export/<format>', methods=['POST'])
def export_chart(format):
    """Export chart in specified format."""
    try:
        session_id = request.json.get('session_id')
        if not session_id or session_id not in session_data:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        chart_type = request.json.get('chart_type', 'waveform')
        export_config = request.json.get('export_config', {})
        
        data = session_data[session_id]['raw_data']
        analysis = session_data[session_id].get('analysis', {})
        config = session_data[session_id].get('chart_config', {})
        
        # Merge export config
        config.update(export_config)
        
        # Generate chart for export
        if format in ['png', 'svg', 'pdf']:
            file_data = chart_generator.export_chart(
                chart_type, data, analysis, config, format
            )
            
            mimetype = {
                'png': 'image/png',
                'svg': 'image/svg+xml',
                'pdf': 'application/pdf'
            }[format]
            
            return send_file(
                io.BytesIO(file_data),
                mimetype=mimetype,
                as_attachment=True,
                download_name=f'flicker_chart.{format}'
            )
        else:
            return jsonify({'success': False, 'error': 'Invalid format'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Recursively discover example CSV files in the top-level CSVs directory."""
    
    try:
        # Base directory containing all example CSVs (mounted/copied into the container)
        base_dir = os.path.abspath(os.path.join(app.root_path, '..', 'CSVs'))
        examples = []
        for root, _dirs, files in os.walk(base_dir):
            for f in files:
                if f.lower().endswith('.csv'):
                    abs_path = os.path.join(root, f)
                    rel_path = os.path.relpath(abs_path, base_dir)
                    # Create a friendly display name – strip extension, replace delimiters with spaces
                    name = os.path.splitext(rel_path)[0].replace('_', ' ').replace('-', ' ').title()
                    examples.append({
                        'path': rel_path.replace('\\', '/'),  # ensure forward slashes for web
                        'name': name
                    })
        # Sort alphabetically by name for nicer UX
        examples.sort(key=lambda x: x['name'])
        return jsonify({'success': True, 'examples': examples})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/example/<path:filepath>', methods=['GET'])
def load_example(filepath):
    """Load a specific example CSV file."""
    try:
        base_dir = os.path.abspath(os.path.join(app.root_path, '..', 'CSVs'))
        # Normalize path to prevent traversal outside base_dir
        safe_rel_path = os.path.normpath(filepath)
        full_path = os.path.abspath(os.path.join(base_dir, safe_rel_path))

        if not full_path.startswith(base_dir):
            return jsonify({'success': False, 'error': 'Invalid path'}), 400

        if not full_path.lower().endswith('.csv'):
            full_path += '.csv'

        if not os.path.exists(full_path):
            return jsonify({'success': False, 'error': 'Example not found'}), 404

        # Read and process the CSV
        with open(full_path, 'r') as f:
            content = f.read()

        data = csv_processor.process_csv_content(content)

        # Create a new session for this example
        session_id = str(uuid.uuid4())
        session_data[session_id] = {
            'raw_data': data,
            'filename': os.path.basename(full_path)
        }

        analysis = flicker_analyzer.analyze(data)
        
        # Store analysis in session
        session_data[session_id]['analysis'] = analysis

        return jsonify({
            'success': True,
            'session_id': session_id,
            'preview': csv_processor.get_preview(data),
            'analysis': analysis
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size limit exceeded."""
    return jsonify({
        'success': False,
        'error': f'File size exceeds maximum allowed size of {app.config["MAX_CONTENT_LENGTH"] / 1024 / 1024}MB'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({
        'success': False,
        'error': 'An internal error occurred. Please try again.'
    }), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Beautiful Flicker Flask Web Application')
    parser.add_argument('--port', '-p', type=int, default=8080,
                        help='Port to run the application on (default: 8080)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                        help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true',
                        help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Override debug setting if specified
    if args.debug:
        app.debug = True
    
    print(f"Starting Beautiful Flicker on http://{args.host}:{args.port}")
    app.run(debug=app.debug, host=args.host, port=args.port)