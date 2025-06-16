from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QLabel, QMenu, QMessageBox, QDialog, QComboBox,
    QLineEdit, QToolBar, QGroupBox, QGridLayout, QTabWidget, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QColor

import psutil
from datetime import datetime

from src.core.process_monitor import ProcessManager
from src.gui.performance_dialog import PerformanceDialog
from src.core.process_monitor_thread import ProcessMonitorThread
from src.core.database_manager import DatabaseManager  # Add this import

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TaskMaster")
        self.setMinimumSize(800, 500)

        self.process_manager = ProcessManager()
        self.db_manager = DatabaseManager()  # Initialize DatabaseManager

        self.process_manager.update_all()

        self.monitor_thread = ProcessMonitorThread(self.process_manager, update_interval=5)
        self.monitor_thread.update_complete.connect(self.on_background_update)
        self.monitor_thread.start()

        self._setup_ui()

        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(2000)
        
        # Add timer for database updates
        self.db_update_timer = QTimer(self)
        self.db_update_timer.timeout.connect(self.update_database)
        self.db_update_timer.start(300000)  # 5 minutes

    def _setup_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #2D3142; color: white;")
        main_layout = QHBoxLayout(central_widget)

        self._create_toolbar()

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.textChanged.connect(self.filter_processes)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #3E4154;
                color: white;
                border: 1px solid #4F5D75;
                border-radius: 3px;
                padding: 3px;
            }
        """)
        search_layout.addWidget(self.search_box)

        start_process_layout = QHBoxLayout()

        button_style = """
            QPushButton {
                background-color: #3E4154;
                color: white;
                border: 1px solid #4F5D75;
                padding: 5px 10px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4F5D75;
            }
            QPushButton:pressed {
                background-color: #5C6B8C;
            }
        """

        self.start_process_button = QPushButton("Start Process")
        self.start_process_button.clicked.connect(self.show_start_process_dialog)
        self.start_process_button.setStyleSheet(button_style)
        start_process_layout.addWidget(self.start_process_button)
        start_process_layout.addStretch()

        search_layout.addStretch()
        search_layout.addWidget(QLabel("Total Processes:"))
        self.total_processes_label = QLabel("0")
        self.total_processes_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        search_layout.addWidget(self.total_processes_label)

        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "User", "CPU %", "Memory %"
        ])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.process_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.process_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_context_menu)
        self.process_table.clicked.connect(self.show_process_info)

        self.process_table.setStyleSheet("""
            QTableWidget {
                background-color: #2D3142;
                color: white;
                gridline-color: #4F5D75;
                border: none;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #4F5D75;
            }
            QHeaderView::section {
                background-color: #3E4154;
                color: white;
                padding: 4px;
                border: 1px solid #4F5D75;
            }
        """)

        left_layout.addLayout(search_layout)
        left_layout.addLayout(start_process_layout)
        left_layout.addWidget(self.process_table)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        info_group = QGroupBox("Process Information")
        info_group.setStyleSheet("""
            QGroupBox {
                background-color: #3E4154;
                color: white;
                border: 1px solid #4F5D75;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 3px;
            }
            QLabel {
                color: white;
            }
        """)
        info_layout = QGridLayout(info_group)

        info_layout.addWidget(QLabel("PID:"), 0, 0)
        self.info_pid_label = QLabel()
        info_layout.addWidget(self.info_pid_label, 0, 1)

        info_layout.addWidget(QLabel("Name:"), 1, 0)
        self.info_name_label = QLabel()
        info_layout.addWidget(self.info_name_label, 1, 1)

        info_layout.addWidget(QLabel("User:"), 2, 0)
        self.info_user_label = QLabel()
        info_layout.addWidget(self.info_user_label, 2, 1)

        info_layout.addWidget(QLabel("Status:"), 3, 0)
        self.info_status_label = QLabel()
        info_layout.addWidget(self.info_status_label, 3, 1)

        info_layout.addWidget(QLabel("CPU Usage:"), 4, 0)
        self.info_cpu_label = QLabel()
        info_layout.addWidget(self.info_cpu_label, 4, 1)

        info_layout.addWidget(QLabel("Memory Usage:"), 5, 0)
        self.info_memory_label = QLabel()
        info_layout.addWidget(self.info_memory_label, 5, 1)

        info_layout.addWidget(QLabel("Threads:"), 6, 0)
        self.info_threads_label = QLabel()
        info_layout.addWidget(self.info_threads_label, 6, 1)

        info_layout.addWidget(QLabel("Created:"), 7, 0)
        self.info_created_label = QLabel()
        info_layout.addWidget(self.info_created_label, 7, 1)

        right_layout.addWidget(info_group)
        right_layout.addStretch()

        main_layout.addWidget(left_panel, 70)
        main_layout.addWidget(right_panel, 30)

        self.setCentralWidget(central_widget)

        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: #3E4154;
                color: white;
                border-top: 1px solid #4F5D75;
            }
        """)

        self._create_menu_bar()

    def _create_toolbar(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #3E4154;
                border: none;
                spacing: 3px;
            }
            QToolButton {
                background-color: #3E4154;
                color: white;
                border: none;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #4F5D75;
            }
        """)
        self.addToolBar(toolbar)

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.update_data)
        refresh_action.setStatusTip("Refresh process list")
        toolbar.addAction(refresh_action)

        performance_action = QAction("Performance", self)
        performance_action.triggered.connect(self.show_performance_dialog)
        performance_action.setStatusTip("Show system performance graphs")
        toolbar.addAction(performance_action)

        toolbar.addSeparator()

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""
            QMenuBar {
                background-color: #3E4154;
                color: white;
            }
            QMenuBar::item {
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #4F5D75;
            }
            QMenu {
                background-color: #3E4154;
                color: white;
                border: 1px solid #4F5D75;
            }
            QMenu::item:selected {
                background-color: #4F5D75;
            }
        """)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        menu_bar.addAction(exit_action)

        help_menu = menu_bar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    @pyqtSlot()
    def update_data(self):
        self.update_ui()

    @pyqtSlot()
    def on_background_update(self):
        pass

    @pyqtSlot()
    def update_ui(self):
        self._update_process_table()

        total_processes = len(psutil.pids())
        self.total_processes_label.setText(str(total_processes))
        self.statusBar().showMessage(f"Showing top 10 processes | Last updated: {datetime.now().strftime('%H:%M:%S')}")

        selected_row = self.process_table.currentRow()
        if selected_row >= 0:
            self.show_process_info()

    def _update_process_table(self):
        process_list = self.process_manager.get_process_list()

        filter_text = self.search_box.text().lower()
        if filter_text:
            process_list = [p for p in process_list if filter_text in p['name'].lower()]

        process_list.sort(key=lambda x: x['cpu_percent'], reverse=True)

        process_list = process_list[:10]

        self.process_table.setRowCount(10)

        for row in range(10):
            for col in range(5):
                self.process_table.setItem(row, col, QTableWidgetItem(""))

        for row, process in enumerate(process_list):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(process['pid'])))

            self.process_table.setItem(row, 1, QTableWidgetItem(process['name']))

            self.process_table.setItem(row, 2, QTableWidgetItem(process['username']))

            cpu_item = QTableWidgetItem(f"{process['cpu_percent']:.1f}")
            cpu_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.process_table.setItem(row, 3, cpu_item)

            total_memory = psutil.virtual_memory().total / (1024 * 1024)
            memory_percent = (process['memory_mb'] / total_memory) * 100
            mem_item = QTableWidgetItem(f"{memory_percent:.1f}")
            mem_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.process_table.setItem(row, 4, mem_item)

            if process['cpu_percent'] > 50:
                for col in range(self.process_table.columnCount()):
                    item = self.process_table.item(row, col)
                    item.setBackground(QColor(120, 60, 60))

    def filter_processes(self):
        self._update_process_table()

    def set_update_interval(self, interval_ms):
        self.update_timer.stop()
        self.update_timer.start(interval_ms)

    def get_selected_pid(self):
        selected_items = self.process_table.selectedItems()
        if not selected_items:
            return None

        row = selected_items[0].row()
        pid_item = self.process_table.item(row, 0)
        return int(pid_item.text())

    @pyqtSlot()
    def terminate_selected_process(self):
        pid = self.get_selected_pid()
        if pid is None:
            QMessageBox.warning(self, "Warning", "No process selected.")
            return

        process = self.process_manager.get_process(pid)
        if not process:
            QMessageBox.warning(self, "Warning", f"Process with PID {pid} not found.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Termination",
            f"Are you sure you want to terminate the process '{process.name}' (PID: {pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.process_manager.terminate_process(pid)
            if success:
                QMessageBox.information(self, "Success", f"Process with PID {pid} terminated successfully.")
                self.update_data()
            else:
                QMessageBox.warning(self, "Error", f"Failed to terminate process with PID {pid}.")

    def show_process_info(self):
        pid = self.get_selected_pid()
        if pid is None:
            self.info_pid_label.setText("")
            self.info_name_label.setText("")
            self.info_user_label.setText("")
            self.info_status_label.setText("")
            self.info_cpu_label.setText("")
            self.info_memory_label.setText("")
            self.info_threads_label.setText("")
            self.info_created_label.setText("")
            return

        process = self.process_manager.get_process(pid)
        if not process:
            return

        self.info_pid_label.setText(str(process.pid))
        self.info_name_label.setText(process.name)
        self.info_user_label.setText(process.username)
        self.info_status_label.setText(process.status)
        self.info_cpu_label.setText(f"{process.cpu_percent:.1f}%")

        total_memory = psutil.virtual_memory().total / (1024 * 1024)
        memory_percent = (process.memory_usage / total_memory) * 100
        self.info_memory_label.setText(f"{memory_percent:.1f}% ({process.memory_usage:.1f} MB)")

        self.info_threads_label.setText(str(process.num_threads))
        self.info_created_label.setText(process.create_time.strftime("%H:%M:%S %d/%m/%Y"))

    def show_priority_dialog(self):
        pid = self.get_selected_pid()
        if pid is None:
            QMessageBox.warning(self, "Warning", "No process selected.")
            return

        process = self.process_manager.get_process(pid)
        if not process:
            QMessageBox.warning(self, "Warning", f"Process with PID {pid} not found.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Set Priority for {process.name} (PID: {pid})")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Select Priority:"))

        priority_combo = QComboBox()

        priorities = [
            ("Realtime", psutil.REALTIME_PRIORITY_CLASS if hasattr(psutil, 'REALTIME_PRIORITY_CLASS') else 256),
            ("High", psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else 128),
            ("Above Normal", psutil.ABOVE_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'ABOVE_NORMAL_PRIORITY_CLASS') else 32768),
            ("Normal", psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 32),
            ("Below Normal", psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 16384),
            ("Low", psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 64),
        ]

        for name, value in priorities:
            priority_combo.addItem(name, value)

        try:
            current_priority = process.process.nice()
            for i, (_, value) in enumerate(priorities):
                if value == current_priority:
                    priority_combo.setCurrentIndex(i)
                    break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        layout.addWidget(priority_combo)

        button_layout = QHBoxLayout()

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(lambda: self._apply_priority(pid, priority_combo.currentData()))

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(apply_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        dialog.exec()

    def _apply_priority(self, pid, priority):
        success = self.process_manager.set_process_priority(pid, priority)
        if success:
            QMessageBox.information(self, "Success", f"Priority changed for process with PID {pid}.")
        else:
            QMessageBox.warning(self, "Error", f"Failed to change priority for process with PID {pid}.")

    def show_context_menu(self, position):
        pid = self.get_selected_pid()
        if pid is None:
            return

        context_menu = QMenu(self)

        end_process_action = QAction("End Process", self)
        end_process_action.triggered.connect(self.terminate_selected_process)
        context_menu.addAction(end_process_action)

        priority_menu = context_menu.addMenu("Set Priority")

        priorities = [
            ("Realtime", psutil.REALTIME_PRIORITY_CLASS if hasattr(psutil, 'REALTIME_PRIORITY_CLASS') else 256),
            ("High", psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else 128),
            ("Above Normal", psutil.ABOVE_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'ABOVE_NORMAL_PRIORITY_CLASS') else 32768),
            ("Normal", psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 32),
            ("Below Normal", psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 16384),
            ("Low", psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 64),
        ]

        for name, value in priorities:
            action = QAction(name, self)
            action.triggered.connect(lambda _, p=value: self.set_process_priority(pid, p))
            priority_menu.addAction(action)

        context_menu.exec(self.process_table.mapToGlobal(position))

    def set_process_priority(self, pid, priority):
        success = self.process_manager.set_process_priority(pid, priority)
        if success:
            QMessageBox.information(self, "Success", f"Priority changed for process with PID {pid}.")
        else:
            QMessageBox.warning(self, "Error", f"Failed to change priority for process with PID {pid}.")

    def show_about_dialog(self):
        # Create a tab widget for the about dialog
        about_tabs = QTabWidget()
        
        # About tab
        about_widget = QWidget()
        about_layout = QVBoxLayout(about_widget)
        about_text = QLabel("""
            <h1>TaskMaster</h1>
            <p>A Solution for Process Control and Optimization</p>
            <p>Version 1.0</p>
            <p>Developed by:</p>
            <ul>
                <li>Ravi Kumar (leader)</li>
                <li>Pratik Rana</li>
                <li>Rohit</li>
            </ul>
            <p>A GUI-based task manager designed to enhance process management and resource utilization.</p>
        """)
        about_text.setOpenExternalLinks(True)
        about_layout.addWidget(about_text)
        about_tabs.addTab(about_widget, "About")
        
        # History tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        
        # Create a table for process history
        history_table = QTableWidget()
        history_table.setColumnCount(5)
        history_table.setHorizontalHeaderLabels(["Timestamp", "PID", "Name", "CPU %", "Memory (MB)"])
        history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Get process history data from database
        history_data = self.db_manager.get_process_history(limit=50)
        
        if not history_data.empty:
            history_table.setRowCount(len(history_data))
            for i, (_, row) in enumerate(history_data.iterrows()):
                history_table.setItem(i, 0, QTableWidgetItem(row['timestamp'].strftime("%H:%M:%S %d/%m/%Y")))
                history_table.setItem(i, 1, QTableWidgetItem(str(row['pid'])))
                history_table.setItem(i, 2, QTableWidgetItem(row['name']))
                history_table.setItem(i, 3, QTableWidgetItem(f"{row['cpu_percent']:.1f}"))
                history_table.setItem(i, 4, QTableWidgetItem(f"{row['memory_mb']:.1f}"))
        else:
            history_table.setRowCount(1)
            history_table.setSpan(0, 0, 1, 5)
            history_table.setItem(0, 0, QTableWidgetItem("No history data available"))
        
        history_layout.addWidget(history_table)
        about_tabs.addTab(history_widget, "Process History")
        
        # Create and show dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("About TaskMaster")
        dialog.setMinimumSize(600, 400)
        
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(about_tabs)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(dialog.accept)
        dialog_layout.addWidget(buttons)
        
        dialog.exec()

    def show_start_process_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Start New Process")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Enter process name or full path:"))
        process_input = QLineEdit()
        process_input.setPlaceholderText("e.g., notepad.exe or C:\\Windows\\System32\\notepad.exe")
        layout.addWidget(process_input)

        button_layout = QHBoxLayout()
        start_button = QPushButton("Start")
        cancel_button = QPushButton("Cancel")

        start_button.clicked.connect(lambda: self.start_process(process_input.text(), dialog))
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(start_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.exec()

    def start_process(self, process_name, dialog):
        if not process_name.strip():
            QMessageBox.warning(self, "Warning", "Please enter a process name or path.")
            return

        try:
            import subprocess
            subprocess.Popen(process_name, shell=True)
            dialog.accept()
            QTimer.singleShot(1000, self.update_data)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start process: {str(e)}")

    def show_performance_dialog(self):
        dialog = PerformanceDialog(self.process_manager, self)
        dialog.exec()

    def closeEvent(self, event):
        if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
            self.monitor_thread.stop()

        event.accept()

    def update_database(self):
        """Store current process and system data in the database."""
        try:
            # Get current process list
            process_list = self.process_manager.get_process_list()
            
            # Store in database
            self.db_manager.store_process_data(process_list)
            
            # Get and store system data
            system_data = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'total_processes': len(psutil.pids())
            }
            self.db_manager.store_system_data(system_data)
        except Exception as e:
            print(f"Error updating database: {e}")


