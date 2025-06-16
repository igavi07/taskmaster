# TaskMaster: A Solution for Process Control and Optimization

A GUI-based task manager designed to enhance process management and resource utilization on operating systems.

## Project Overview

TaskMaster is a comprehensive task manager application that provides real-time monitoring of system processes, resource usage, and process control capabilities. It aims to address inefficiencies in existing task management solutions by offering detailed process information, resource tracking, and an intuitive user interface.

## Team Members

- Ravi Kumar (Team Leader)
- Rohit Chauhan
- Pratik Rana  

## Features

- Real-time monitoring of active processes and their states
- Detailed resource usage tracking (CPU, memory, disk, network)
- Process control capabilities (start, stop, modify priorities)
- Responsive GUI built with Python and PyQt6
- System logging and analytics using SQLite
- Performance visualization with Matplotlib
- Efficient design with minimal resource overhead

## Project Structure

```
TaskMaster/
├── main.py                  # Main entry point
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
├── src/                     # Source code
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── process_monitor.py  # Process monitoring
│   │   └── data_storage.py     # Data storage and retrieval
│   └── gui/                 # User interface
│       ├── __init__.py
│       ├── main_window.py      # Main application window
│       ├── process_detail_dialog.py  # Process details dialog
│       ├── system_monitor_widget.py  # System monitor widget
│       └── charts_widget.py    # Performance charts
└── data/                    # Data storage directory
    └── taskmaster.db        # SQLite database (created at runtime)
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/taskmaster.git
   cd taskmaster
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python main.py
   ```

## Requirements

- Python 3.8 or higher
- PyQt6
- psutil
- matplotlib
- SQLite3

## Development Timeline

1. **Week 1-2**: Research and Planning
   - Requirements gathering
   - Technology selection
   - Architecture design

2. **Week 3-4**: Core Development
   - Process monitoring implementation
   - Resource tracking
   - Data storage

3. **Week 5-6**: GUI Integration
   - Main interface development
   - Process details view
   - Charts and visualizations

4. **Week 7**: Optimization and Testing
   - Performance optimization
   - Bug fixing
   - Cross-platform testing

5. **Week 8**: Finalization
   - Documentation
   - Final testing
   - Project presentation

## License

This project is created for educational purposes as part of a course requirement.

## Acknowledgments

- Course instructors and teaching assistants
- Open-source libraries used in this project
