# Beautiful Flicker - Quick Start Guide

## 🚀 Fastest Way to Start

### macOS/Linux
```bash
./run.sh
```
App will start on http://localhost:8080

### Windows
```cmd
run.bat
```
App will start on http://localhost:8080

### Custom Port
```bash
# macOS/Linux
./run.sh 3000

# Windows
run.bat 3000
```

## 📊 First Steps

1. **Upload Data**
   - Drag and drop a CSV file onto the upload area
   - OR click "Select an example" and choose one

2. **View Results**
   - Flicker metrics appear automatically
   - Standards compliance shown with color coding

3. **Customize Chart**
   - Add a title
   - Toggle metrics display
   - Switch between chart types

4. **Export**
   - Choose format (PNG, SVG, PDF)
   - Click "Export Chart"

## 📁 CSV Format

Your CSV should have two columns:
```csv
Time,Value
0.000,0.95
0.001,0.97
0.002,0.98
```

Accepted column names:
- Time: `time`, `t`, `seconds`, `s`
- Value: `voltage`, `value`, `light`, `v`

## 🔧 Common Issues

### Port Already in Use
```bash
# Use a different port
./run.sh 9000
```

### Docker Not Running
Make sure Docker Desktop is running before starting the app.

### Slow First Start
The first run downloads dependencies. Subsequent runs are much faster.

## 📚 More Information

See the full [README.md](README.md) for:
- API documentation
- Development setup
- Production deployment
- Command-line tools