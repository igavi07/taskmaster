"""
Process detail dialog module for TaskMaster.
Displays detailed information about a selected process.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QGroupBox, QGridLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont

import psutil
from datetime import datetime

class ProcessDetailDialog(QDialog):
    """Dialog for displaying detailed process information."""

    def __init__(self, process, parent=None):
        """Initialize the dialog with a process."""
        super().__init__(parent)

        self.process = process
        self.setWindowTitle(f"Process Details: {process.name} (PID: {process.pid})")
        self.setMinimumSize(600, 400)

        # Set up the UI
        self._setup_ui()

        # Set up timer for updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)  # Update every 5 seconds

        # Initial update
        self.update_data()

    def _setup_ui(self):
        """Set up the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()

        # Create general tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)

        # Process information group
        info_group = QGroupBox("Process Information")
        info_layout = QGridLayout(info_group)

        # Add labels for process information
        info_layout.addWidget(QLabel("Name:"), 0, 0)
        self.name_label = QLabel()
        info_layout.addWidget(self.name_label, 0, 1)

        info_layout.addWidget(QLabel("PID:"), 1, 0)
        self.pid_label = QLabel()
        info_layout.addWidget(self.pid_label, 1, 1)

        info_layout.addWidget(QLabel("Status:"), 2, 0)
        self.status_label = QLabel()
        info_layout.addWidget(self.status_label, 2, 1)

        info_layout.addWidget(QLabel("User:"), 3, 0)
        self.user_label = QLabel()
        info_layout.addWidget(self.user_label, 3, 1)

        info_layout.addWidget(QLabel("Started:"), 4, 0)
        self.started_label = QLabel()
        info_layout.addWidget(self.started_label, 4, 1)

        # Removed command line arguments display for simplicity

        # Resource usage group
        resource_group = QGroupBox("Resource Usage")
        resource_layout = QGridLayout(resource_group)

        resource_layout.addWidget(QLabel("CPU Usage:"), 0, 0)
        self.cpu_layout = QHBoxLayout()
        self.cpu_label = QLabel()
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_layout.addWidget(self.cpu_label)
        self.cpu_layout.addWidget(self.cpu_bar)
        resource_layout.addLayout(self.cpu_layout, 0, 1)

        resource_layout.addWidget(QLabel("Memory Usage:"), 1, 0)
        self.memory_layout = QHBoxLayout()
        self.memory_label = QLabel()
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        self.memory_layout.addWidget(self.memory_label)
        self.memory_layout.addWidget(self.memory_bar)
        resource_layout.addLayout(self.memory_layout, 1, 1)

        resource_layout.addWidget(QLabel("Threads:"), 2, 0)
        self.threads_label = QLabel()
        resource_layout.addWidget(self.threads_label, 2, 1)

        # Add groups to general layout
        general_layout.addWidget(info_group)
        general_layout.addWidget(resource_group)

        # Create threads tab with simplified view
        threads_tab = QWidget()
        threads_layout = QVBoxLayout(threads_tab)

        # Add a simple label showing thread count
        threads_layout.addWidget(QLabel("Thread Information"))
        self.thread_count_label = QLabel()
        self.thread_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thread_count_label.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        threads_layout.addWidget(self.thread_count_label)

        # Create memory tab
        memory_tab = QWidget()
        memory_layout = QVBoxLayout(memory_tab)

        self.memory_table = QTableWidget()
        self.memory_table.setColumnCount(2)
        self.memory_table.setHorizontalHeaderLabels(["Type", "Value"])
        self.memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.memory_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        memory_layout.addWidget(self.memory_table)

        # Add tabs to tab widget with clearer labels
        self.tab_widget.addTab(general_tab, "Process Overview")
        self.tab_widget.addTab(threads_tab, "Thread Info")
        self.tab_widget.addTab(memory_tab, "Memory Usage")

        # Add tab widget to main layout
        main_layout.addWidget(self.tab_widget)

        # Add buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_data)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)

        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)

        main_layout.addLayout(button_layout)

    @pyqtSlot()
    def update_data(self):
        """Update all data in the dialog."""
        try:
            # Update process information
            self.process.update()

            if not self.process.is_running:
                self.update_timer.stop()
                self.setWindowTitle(f"Process Details: {self.process.name} (PID: {self.process.pid}) - TERMINATED")
                return

            # Update general information
            self.name_label.setText(self.process.name)
            self.pid_label.setText(str(self.process.pid))
            self.status_label.setText(self.process.status)
            self.user_label.setText(self.process.username)
            self.started_label.setText(self.process.create_time.strftime("%H:%M:%S %d/%m/%Y"))
            # Command line display removed for simplicity

            # Update resource usage
            self.cpu_label.setText(f"{self.process.cpu_percent:.1f}%")
            self.cpu_bar.setValue(int(self.process.cpu_percent))

            self.memory_label.setText(f"{self.process.memory_usage:.1f} MB")
            # Set memory bar to percentage of system memory
            total_memory = psutil.virtual_memory().total / (1024 * 1024)  # MB
            memory_percent = (self.process.memory_usage / total_memory) * 100
            self.memory_bar.setValue(int(memory_percent))

            self.threads_label.setText(str(self.process.num_threads))

            # Update thread count display
            self.thread_count_label.setText(f"{self.process.num_threads} threads running")

            # Update memory table
            self._update_memory_table()

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            self.update_timer.stop()
            self.setWindowTitle(f"Process Details: {self.process.name} (PID: {self.process.pid}) - TERMINATED")

    # Thread table update method removed - simplified interface

    def _update_memory_table(self):
        """Update the memory table."""
        try:
            memory_info = self.process.process.memory_info()
            memory_types = [
                ("RSS (Resident Set Size)", memory_info.rss / (1024 * 1024), "MB"),
                ("VMS (Virtual Memory Size)", memory_info.vms / (1024 * 1024), "MB"),
            ]

            # Add platform-specific memory info
            if hasattr(memory_info, 'shared'):
                memory_types.append(("Shared", memory_info.shared / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'text'):
                memory_types.append(("Text", memory_info.text / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'data'):
                memory_types.append(("Data", memory_info.data / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'lib'):
                memory_types.append(("Lib", memory_info.lib / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'dirty'):
                memory_types.append(("Dirty", memory_info.dirty / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'uss'):
                memory_types.append(("USS (Unique Set Size)", memory_info.uss / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'pss'):
                memory_types.append(("PSS (Proportional Set Size)", memory_info.pss / (1024 * 1024), "MB"))
            if hasattr(memory_info, 'swap'):
                memory_types.append(("Swap", memory_info.swap / (1024 * 1024), "MB"))

            self.memory_table.setRowCount(len(memory_types))

            for row, (name, value, unit) in enumerate(memory_types):
                # Type
                self.memory_table.setItem(row, 0, QTableWidgetItem(name))

                # Value
                value_item = QTableWidgetItem(f"{value:.2f} {unit}")
                value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.memory_table.setItem(row, 1, value_item)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
