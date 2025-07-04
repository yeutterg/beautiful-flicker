# Beautiful Flicker

A modern Flask web application for lighting flicker data analysis and visualization, featuring a brutalist/minimalist design aesthetic.

![Beautiful Flicker Screenshot](docs/images/screenshot.png)

## Features

### Core Functionality
- **Flicker Analysis**: Comprehensive analysis of lighting flicker waveforms
- **Standards Compliance**: Automatic checking against IEEE 1789-2015, California JA8, and WELL v2 standards
- **Multiple Visualizations**: 
  - Time-domain waveform plots
  - IEEE PAR 1789-2015 compliance graphics
  - FFT spectrum analysis
  - Statistical distribution histograms

### User Interface
- **Brutalist Design**: Clean, minimalist interface inspired by restfullighting.com
- **Drag-and-Drop Upload**: Easy CSV file upload with visual feedback
- **Real-time Configuration**: Interactive chart customization
- **Multiple Export Formats**: PNG, SVG, and PDF export with customizable resolution

### Data Input Options
- File upload (CSV/TXT, up to 50MB)
- Direct CSV paste
- Pre-loaded example datasets
- Flexible column detection

## Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git (to clone the repository)

### Running the Application

1. Clone the repository:
```bash
git clone https://github.com/yeutterg/beautiful-flicker.git
cd beautiful-flicker
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```

3. Access the application at `http://localhost:8080`

### Using a Custom Port

The application runs on port 8080 by default. To use a different port:

**With Docker Compose:**
```bash
# Use port 3000
PORT=3000 docker-compose up

# Or set in .env file
echo "PORT=3000" >> .env
docker-compose up
```

**With Docker directly:**
```bash
# Build the image
docker build -t beautiful-flicker .

# Run on port 3000
docker run -p 3000:8080 -e PORT=8080 beautiful-flicker
```

**For development (without Docker):**
```bash
cd flask_app
python app.py --port 3000

# Or use short form
python app.py -p 3000

# Additional options
python app.py --help
```

### Docker Commands

**Start the application:**
```bash
docker-compose up -d
```

**Stop the application:**
```bash
docker-compose down
```

**View logs:**
```bash
docker-compose logs -f
```

**Rebuild after changes:**
```bash
docker-compose up --build
```

### Environment Variables

Create a `.env` file for production settings:
```env
PORT=8080
SECRET_KEY=your-secure-secret-key-here
FLASK_ENV=production
MAX_UPLOAD_SIZE=52428800
```

## Development Setup

### Local Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r flask_app/requirements.txt
```

3. Run the development server:
```bash
cd flask_app
python app.py

# With custom port
python app.py --port 3000

# With debug mode
python app.py --debug

# Bind to specific host
python app.py --host 127.0.0.1 --port 3000
```

### Development with Docker

For development with hot-reloading, uncomment the volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./flask_app:/app/flask_app
  - ./src:/app/src
```

Then run:
```bash
docker-compose up
```

## Usage Guide

### Uploading Data

1. **Drag and Drop**: Simply drag a CSV file onto the upload area
2. **Click to Browse**: Click the upload area to select a file
3. **Paste Data**: Paste CSV data directly into the text area
4. **Load Example**: Select from pre-loaded example datasets

### CSV Format

The application accepts CSV files with time and value columns. Supported column names include:
- Time columns: `time`, `t`, `x`, `seconds`, `s`
- Value columns: `voltage`, `value`, `light`, `y`, `v`, `intensity`

Example format:
```csv
Time,Value
0.000,0.95
0.001,0.97
0.002,0.98
```

### Chart Configuration

- **Basic Settings**: Customize title, font, and text sizes
- **Overlays**: Toggle flicker metrics and standards compliance displays
- **Chart Types**: Switch between waveform, IEEE compliance, FFT, and histogram views

### Exporting Results

1. Select export format (PNG, SVG, or PDF)
2. Choose resolution (screen, print, or custom DPI)
3. Set size preset or custom dimensions
4. Click "Export Chart" to download

## API Documentation

### Base URL
```
http://localhost:8080/api
```

### Endpoints

- `POST /api/upload` - Upload CSV file or paste data
- `POST /api/analyze` - Perform detailed analysis
- `POST /api/configure` - Update chart configuration
- `POST /api/chart/{type}` - Generate specific chart type
- `GET /api/export/{format}` - Export chart in specified format
- `GET /api/examples` - List available examples
- `GET /api/example/{filename}` - Load specific example

### Example API Usage

```javascript
// Upload file
const formData = new FormData();
formData.append('file', csvFile);

fetch('http://localhost:8080/api/upload', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

```python
# Python example
import requests

# Upload CSV file
with open('data.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8080/api/upload',
        files={'file': f}
    )
    result = response.json()
    session_id = result['session_id']

# Generate chart
chart_response = requests.post(
    'http://localhost:8080/api/chart/waveform',
    json={'session_id': session_id}
)
```

## Command Line Tools

The original command-line tools are still available in the `src` directory:

```python
from src.waveform import Waveform

# Load and analyze a waveform
waveform = Waveform('data.csv', 'My Light Source')
print(f"Frequency: {waveform.get_frequency()} Hz")
print(f"Percent Flicker: {waveform.get_percent_flicker()}%")
print(f"IEEE 1789-2015: {waveform.get_ieee_1789_2015()}")

# Generate a plot
waveform.plot(filename='output.png')
```

## Project Structure

```
beautiful-flicker/
├── flask_app/              # Flask web application
│   ├── app.py             # Main Flask application
│   ├── config.py          # Configuration settings
│   ├── requirements.txt   # Python dependencies
│   ├── static/            # Frontend assets
│   │   ├── css/          # Brutalist styling
│   │   └── js/           # Frontend JavaScript
│   ├── templates/         # HTML templates
│   └── modules/           # Backend modules
│       ├── flicker_analysis.py
│       ├── visualization.py
│       └── data_processing.py
├── src/                   # Original analysis tools
│   ├── waveform.py       # Core waveform analysis
│   ├── plot.py           # Plotting functions
│   ├── standards.py      # Standards compliance
│   └── utils.py          # Utility functions
├── docker-compose.yml     # Docker Compose config
├── Dockerfile            # Docker image definition
└── README.md             # This file
```

## Production Deployment

### Using Docker Compose (Recommended)

1. Clone the repository on your server
2. Create a `.env` file with production settings:
   ```env
   PORT=80
   SECRET_KEY=your-production-secret-key
   FLASK_ENV=production
   ```
3. Run: `docker-compose up -d`

### Using a Reverse Proxy

For production, it's recommended to use a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Scaling

The Docker configuration includes 4 Gunicorn workers by default. Adjust based on your server's CPU cores:

```dockerfile
CMD gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 4 --timeout 120 flask_app.app:app
```

## Standards References

- **IEEE 1789-2015**: [Standard](http://www.bio-licht.org/02_resources/info_ieee_2015_standards-1789.pdf)
- **WELL Building Standard**: [L07 P2](https://v2.wellcertified.com/v/en/light/feature/7)
- **California JA8**: [2019 Standard](https://efiling.energy.ca.gov/GetDocument.aspx?tn=223245-9&DocumentContentId=27701)

## Troubleshooting

### Port Already in Use
If you get a "port already in use" error:
```bash
# Find what's using the port
lsof -i :8080  # On macOS/Linux
netstat -ano | findstr :8080  # On Windows

# Use a different port
PORT=8081 docker-compose up
```

### Docker Build Issues
```bash
# Clean rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Permission Issues
If you encounter permission issues with Docker:
```bash
# Add your user to the docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript
- Add tests for new features
- Update documentation as needed

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

For custom versions and testing services: [gregyeutter@gmail.com](mailto:gregyeutter@gmail.com?subject=Beautiful%20Flicker%20Inquiry)

## Acknowledgments

- Original Beautiful Flicker command-line tools
- Brutalist design inspiration from restfullighting.com
- IEEE, WELL, and California standards organizations

## Changelog

### v2.0.0 (2025)
- Complete Flask web application rewrite
- Brutalist/minimalist UI design
- Docker support with configurable ports
- RESTful API for programmatic access
- Multiple export formats (PNG, SVG, PDF)
- Real-time chart configuration
- FFT spectrum analysis
- Statistical distribution plots

### v1.0.0 (Original)
- Command-line tools for flicker analysis
- Jupyter notebook examples
- Basic plotting capabilities