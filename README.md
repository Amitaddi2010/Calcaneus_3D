# Calcaneus Screw Placement Analysis

A web application for orthopedic surgeons to analyze and visualize screw placements in calcaneus (heel bone) surfaces using STL files.

## Features

- Automatic detection of left/right foot
- Breach detection for medial and lateral walls
- Distance measurements between screws and bone surfaces
- Interactive 3D visualization
- Batch processing for multiple screws
- Excel export functionality
- Patient record management
- Comprehensive reporting

## Requirements

- Python 3.11 or higher
- Streamlit
- NumPy
- Pandas
- Matplotlib
- Plotly
- OpenPyXL
- SQLAlchemy
- Trimesh

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/CalcaneusAnalyzer.git
cd CalcaneusAnalyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python init_db.py
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to http://localhost:8501

3. Follow the on-screen instructions to:
   - Upload medial and lateral STL files
   - Upload a ZIP file containing screw STL files
   - Process and analyze screw placements
   - View interactive 3D visualizations
   - Export results to Excel

## Project Structure

- `app.py`: Main Streamlit application
- `database.py`: Database models and operations
- `processing.py`: Screw placement analysis logic
- `visualization.py`: 3D visualization functions
- `utils.py`: Utility functions
- `init_db.py`: Database initialization script

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 