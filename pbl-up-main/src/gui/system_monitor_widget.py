"""
System monitor widget module for TaskMaster.
Displays system resource usage information.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout,
    QLabel, QProgressBar, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SystemMonitorWidget(QWidget):
    """Widget for displaying system resource usage."""
    
    def __init__(self, parent=None):
        """Initialize the system monitor widget."""
        super().__init__(parent)
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        
        # CPU group
        cpu_group = QGroupBox("CPU Usage")
        cpu_layout = QVBoxLayout(cpu_group)
        
        # Overall CPU usage
        overall_cpu_layout = QHBoxLayout()
        overall_cpu_layout.addWidget(QLabel("Overall CPU Usage:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        overall_cpu_layout.addWidget(self.cpu_bar)
        self.cpu_percent_label = QLabel("0%")
        self.cpu_percent_label.setMinimumWidth(50)
        overall_cpu_layout.addWidget(self.cpu_percent_label)
        
        cpu_layout.addLayout(overall_cpu_layout)
        
        # CPU info
        cpu_info_layout = QGridLayout()
        
        cpu_info_layout.addWidget(QLabel("CPU Count:"), 0, 0)
        self.cpu_count_label = QLabel()
        cpu_info_layout.addWidget(self.cpu_count_label, 0, 1)
        
        cpu_info_layout.addWidget(QLabel("CPU Frequency:"), 1, 0)
        self.cpu_freq_label = QLabel()
        cpu_info_layout.addWidget(self.cpu_freq_label, 1, 1)
        
        cpu_layout.addLayout(cpu_info_layout)
        
        # Memory group
        memory_group = QGroupBox("Memory Usage")
        memory_layout = QVBoxLayout(memory_group)
        
        # Overall memory usage
        overall_memory_layout = QHBoxLayout()
        overall_memory_layout.addWidget(QLabel("Memory Usage:"))
        self.memory_bar = QProgressBar()
        self.memory_bar.setRange(0, 100)
        overall_memory_layout.addWidget(self.memory_bar)
        self.memory_percent_label = QLabel("0%")
        self.memory_percent_label.setMinimumWidth(50)
        overall_memory_layout.addWidget(self.memory_percent_label)
        
        memory_layout.addLayout(overall_memory_layout)
        
        # Memory info
        memory_info_layout = QGridLayout()
        
        memory_info_layout.addWidget(QLabel("Total Memory:"), 0, 0)
        self.total_memory_label = QLabel()
        memory_info_layout.addWidget(self.total_memory_label, 0, 1)
        
        memory_info_layout.addWidget(QLabel("Available Memory:"), 1, 0)
        self.available_memory_label = QLabel()
        memory_info_layout.addWidget(self.available_memory_label, 1, 1)
        
        memory_info_layout.addWidget(QLabel("Used Memory:"), 2, 0)
        self.used_memory_label = QLabel()
        memory_info_layout.addWidget(self.used_memory_label, 2, 1)
        
        memory_layout.addLayout(memory_info_layout)
        
        # Disk group
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout(disk_group)
        
        # Overall disk usage
        overall_disk_layout = QHBoxLayout()
        overall_disk_layout.addWidget(QLabel("Disk Usage:"))
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        overall_disk_layout.addWidget(self.disk_bar)
        self.disk_percent_label = QLabel("0%")
        self.disk_percent_label.setMinimumWidth(50)
        overall_disk_layout.addWidget(self.disk_percent_label)
        
        disk_layout.addLayout(overall_disk_layout)
        
        # Disk info
        disk_info_layout = QGridLayout()
        
        disk_info_layout.addWidget(QLabel("Total Disk Space:"), 0, 0)
        self.total_disk_label = QLabel()
        disk_info_layout.addWidget(self.total_disk_label, 0, 1)
        
        disk_info_layout.addWidget(QLabel("Used Disk Space:"), 1, 0)
        self.used_disk_label = QLabel()
        disk_info_layout.addWidget(self.used_disk_label, 1, 1)
        
        disk_info_layout.addWidget(QLabel("Free Disk Space:"), 2, 0)
        self.free_disk_label = QLabel()
        disk_info_layout.addWidget(self.free_disk_label, 2, 1)
        
        disk_layout.addLayout(disk_info_layout)
        
        # Network group
        network_group = QGroupBox("Network Usage")
        network_layout = QGridLayout(network_group)
        
        network_layout.addWidget(QLabel("Bytes Sent:"), 0, 0)
        self.bytes_sent_label = QLabel()
        network_layout.addWidget(self.bytes_sent_label, 0, 1)
        
        network_layout.addWidget(QLabel("Bytes Received:"), 1, 0)
        self.bytes_recv_label = QLabel()
        network_layout.addWidget(self.bytes_recv_label, 1, 1)
        
        network_layout.addWidget(QLabel("Packets Sent:"), 2, 0)
        self.packets_sent_label = QLabel()
        network_layout.addWidget(self.packets_sent_label, 2, 1)
        
        network_layout.addWidget(QLabel("Packets Received:"), 3, 0)
        self.packets_recv_label = QLabel()
        network_layout.addWidget(self.packets_recv_label, 3, 1)
        
        # Add groups to main layout
        main_layout.addWidget(cpu_group)
        main_layout.addWidget(memory_group)
        main_layout.addWidget(disk_group)
        main_layout.addWidget(network_group)
        
        # Add stretch to push everything to the top
        main_layout.addStretch()
    
    def update_data(self, system_monitor):
        """Update the widget with system monitor data."""
        # Update CPU information
        self.cpu_bar.setValue(int(system_monitor.cpu_percent))
        self.cpu_percent_label.setText(f"{system_monitor.cpu_percent:.1f}%")
        
        self.cpu_count_label.setText(f"{system_monitor.cpu_count} cores")
        
        if system_monitor.cpu_freq:
            freq_text = f"{system_monitor.cpu_freq.current:.2f} MHz"
            if hasattr(system_monitor.cpu_freq, 'min') and system_monitor.cpu_freq.min:
                freq_text += f" (Min: {system_monitor.cpu_freq.min:.2f} MHz"
            if hasattr(system_monitor.cpu_freq, 'max') and system_monitor.cpu_freq.max:
                freq_text += f", Max: {system_monitor.cpu_freq.max:.2f} MHz)"
            self.cpu_freq_label.setText(freq_text)
        else:
            self.cpu_freq_label.setText("N/A")
        
        # Update memory information
        self.memory_bar.setValue(int(system_monitor.memory_percent))
        self.memory_percent_label.setText(f"{system_monitor.memory_percent:.1f}%")
        
        self.total_memory_label.setText(f"{system_monitor.total_memory:.2f} GB")
        self.available_memory_label.setText(f"{system_monitor.available_memory:.2f} GB")
        
        used_memory = system_monitor.total_memory - system_monitor.available_memory
        self.used_memory_label.setText(f"{used_memory:.2f} GB")
        
        # Update disk information
        self.disk_bar.setValue(int(system_monitor.disk_percent))
        self.disk_percent_label.setText(f"{system_monitor.disk_percent:.1f}%")
        
        self.total_disk_label.setText(f"{system_monitor.disk_total:.2f} GB")
        self.used_disk_label.setText(f"{system_monitor.disk_used:.2f} GB")
        
        free_disk = system_monitor.disk_total - system_monitor.disk_used
        self.free_disk_label.setText(f"{free_disk:.2f} GB")
        
        # Update network information
        self.bytes_sent_label.setText(self._format_bytes(system_monitor.net_io.bytes_sent))
        self.bytes_recv_label.setText(self._format_bytes(system_monitor.net_io.bytes_recv))
        self.packets_sent_label.setText(f"{system_monitor.net_io.packets_sent:,}")
        self.packets_recv_label.setText(f"{system_monitor.net_io.packets_recv:,}")
    
    def _format_bytes(self, bytes_value):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
        return f"{bytes_value:.2f} PB"
