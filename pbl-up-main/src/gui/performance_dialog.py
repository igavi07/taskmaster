"""
Performance dialog module for TaskMaster.
Displays system performance charts in a dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer

from src.gui.charts_widget import ChartsWidget

class PerformanceDialog(QDialog):
    """Dialog for displaying system performance charts."""

    def __init__(self, process_manager, parent=None):
        """Initialize the performance dialog."""
        super().__init__(parent)

        self.process_manager = process_manager
        self.setWindowTitle("System Performance")
        self.resize(800, 600)

        # Set up the UI
        self._setup_ui()

        # Set up timer for updates - use a faster update rate for smoother graphs
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_charts)
        self.update_timer.start(2000)  # Update every 2 seconds for smoother graphs

        # Track if dialog is visible to avoid unnecessary updates
        self.is_visible = False

        # Initial update
        self.update_charts()

    def _setup_ui(self):
        """Set up the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add title
        title_label = QLabel("System Performance Monitor")
        title_label.setFont(title_label.font())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        main_layout.addWidget(title_label)

        # Add charts widget
        self.charts_widget = ChartsWidget(self)
        main_layout.addWidget(self.charts_widget)

        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #3E4154;
                color: white;
                border: 1px solid #4F5D75;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4F5D75;
            }
            QPushButton:pressed {
                background-color: #5C6B8C;
            }
        """)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)

        # Set dark theme
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

    def update_charts(self):
        """Update the charts with current system data."""
        # Only update if dialog is visible to save resources
        if self.is_visible:
            self.charts_widget.update_data(self.process_manager.system_monitor)

    def showEvent(self, event):
        """Handle dialog show event."""
        self.is_visible = True
        super().showEvent(event)

    def hideEvent(self, event):
        """Handle dialog hide event."""
        self.is_visible = False
        super().hideEvent(event)

    def closeEvent(self, event):
        """Handle dialog close event."""
        self.update_timer.stop()
        event.accept()
