from PyQt6.QtCore import QThread, pyqtSignal
import time

class ProcessMonitorThread(QThread):
    update_complete = pyqtSignal()

    def __init__(self, process_manager, update_interval=5):
        super().__init__()
        self.process_manager = process_manager
        self.update_interval = update_interval
        self.running = True

    def run(self):
        while self.running:
            try:
                self.process_manager.update_all()

                self.update_complete.emit()

                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in process monitor thread: {e}")
                time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()
