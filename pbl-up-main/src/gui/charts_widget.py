from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import deque
import time

plt_style = {
    'axes.facecolor': '#2D2D30',
    'figure.facecolor': '#2D2D30',
    'text.color': 'white',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'grid.color': '#444444',
    'grid.linestyle': '--',
    'grid.linewidth': 0.5
}
matplotlib.rcParams.update(plt_style)

class PerformanceGraph(QWidget):

    def __init__(self, title, color='blue', max_points=100, y_max=100, parent=None):
        super().__init__(parent)

        self.title = title
        self.color = color
        self.max_points = max_points
        self.y_max = y_max

        self.times = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.start_time = time.time()

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(self.title)
        title_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(title_label)

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_ylim(0, self.y_max)
        self.ax.set_xlim(0, 60)
        self.ax.grid(True, alpha=0.3)

        self.ax.set_facecolor('#2D2D30')
        self.figure.patch.set_facecolor('#2D2D30')

        self.line, = self.ax.plot([], [], color=self.color, linewidth=1.5)

        layout.addWidget(self.canvas)

        value_layout = QHBoxLayout()
        value_layout.addWidget(QLabel('Current:'))
        self.current_value_label = QLabel('0.0')
        self.current_value_label.setFont(QFont('Arial', 9, QFont.Weight.Bold))
        self.current_value_label.setStyleSheet(f"color: {self.color};")
        value_layout.addWidget(self.current_value_label)
        value_layout.addStretch()

        value_layout.addWidget(QLabel('Average:'))
        self.avg_value_label = QLabel('0.0')
        self.avg_value_label.setFont(QFont('Arial', 9))
        value_layout.addWidget(self.avg_value_label)
        value_layout.addStretch()

        value_layout.addWidget(QLabel('Max:'))
        self.max_value_label = QLabel('0.0')
        self.max_value_label.setFont(QFont('Arial', 9))
        value_layout.addWidget(self.max_value_label)

        layout.addLayout(value_layout)

        self.figure.tight_layout(pad=0.5)

    def update_data(self, value):
        current_time = time.time() - self.start_time
        self.times.append(current_time)
        self.values.append(value)

        if len(self.times) > self.max_points:
            self.times.popleft()
            self.values.popleft()

        self.line.set_data(self.times, self.values)

        if current_time > self.ax.get_xlim()[1]:
            self.ax.set_xlim(current_time - 60, current_time)

        if hasattr(self, '_update_counter'):
            self._update_counter += 1
        else:
            self._update_counter = 0

        if self._update_counter % 5 == 0:
            self.figure.canvas.draw_idle()
            self.figure.canvas.flush_events()

        self.current_value_label.setText(f'{value:.1f}')

        if len(self.values) > 0:
            avg_value = sum(self.values) / len(self.values)
            max_value = max(self.values)
            self.avg_value_label.setText(f'{avg_value:.1f}')
            self.max_value_label.setText(f'{max_value:.1f}')


class ChartsWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cpu_history = []
        self.memory_history = []
        self.disk_history = []

        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        self.cpu_graph = PerformanceGraph("CPU Usage (%)", color='#4287f5', y_max=100)
        grid_layout.addWidget(self.cpu_graph, 0, 0)

        self.memory_graph = PerformanceGraph("Memory Usage (%)", color='#f54242', y_max=100)
        grid_layout.addWidget(self.memory_graph, 0, 1)

        self.disk_graph = PerformanceGraph("Disk Usage (%)", color='#42f554', y_max=100)
        grid_layout.addWidget(self.disk_graph, 1, 0, 1, 2)

        main_layout.addLayout(grid_layout)

        self.setStyleSheet("background-color: #1E1E1E; color: white;")

    def update_data(self, system_monitor):
        try:
            self.cpu_graph.update_data(system_monitor.cpu_percent)

            self.memory_graph.update_data(system_monitor.memory_percent)

            self.disk_graph.update_data(system_monitor.disk_percent)
        except Exception as e:
            print(f"Error updating charts: {e}")
