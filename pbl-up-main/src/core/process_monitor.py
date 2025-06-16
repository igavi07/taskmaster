import psutil
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class ProcessInfo:
    def __init__(self, pid: int):
        self.pid = pid
        self.process = psutil.Process(pid)
        self.update()

    def update(self) -> None:
        try:
            self.name = self.process.name()
            self.status = self.process.status()
            self.username = self.process.username()
            self.create_time = datetime.fromtimestamp(self.process.create_time())

            self.cpu_percent = self.process.cpu_percent(interval=None)
            mem_info = self.process.memory_info()
            self.memory_usage = mem_info.rss / (1024 * 1024)

            self.num_threads = self.process.num_threads()

            self.cmdline = self.process.cmdline()
            self.exe = self.process.exe()

            self.is_running = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            self.is_running = False

    def terminate(self) -> bool:
        try:
            self.process.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def set_priority(self, priority: int) -> bool:
        try:
            self.process.nice(priority)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False


class SystemMonitor:
    def __init__(self):
        self.update()

    def update(self) -> None:
        self.cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_count = psutil.cpu_count()
        self.cpu_freq = psutil.cpu_freq()

        mem = psutil.virtual_memory()
        self.total_memory = mem.total / (1024 * 1024 * 1024)
        self.available_memory = mem.available / (1024 * 1024 * 1024)
        self.memory_percent = mem.percent

        disk = psutil.disk_usage('/')
        self.disk_total = disk.total / (1024 * 1024 * 1024)
        self.disk_used = disk.used / (1024 * 1024 * 1024)
        self.disk_percent = disk.percent

        self.net_io = psutil.net_io_counters()


class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.system_monitor = SystemMonitor()

    def update_all(self) -> None:
        self.system_monitor.update()

        process_data = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                process_data.append((proc.info['pid'], proc.info['cpu_percent'] or 0))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        process_data.sort(key=lambda x: x[1], reverse=True)
        top_pids = set(pid for pid, _ in process_data[:50])

        for pid in list(self.processes.keys()):
            if pid not in top_pids or not self.processes[pid].is_running:
                del self.processes[pid]

        for pid in top_pids:
            if pid not in self.processes:
                try:
                    self.processes[pid] = ProcessInfo(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            else:
                self.processes[pid].update()

    def get_process_list(self) -> List[Dict[str, Any]]:
        process_list = []
        for pid, process in self.processes.items():
            if process.is_running:
                process_info = {
                    'pid': pid,
                    'name': process.name,
                    'status': process.status,
                    'cpu_percent': process.cpu_percent,
                    'memory_mb': process.memory_usage,
                    'threads': process.num_threads,
                    'username': process.username,
                    'start_time': process.create_time
                }
                process_list.append(process_info)
        return process_list

    def get_process(self, pid: int) -> Optional[ProcessInfo]:
        return self.processes.get(pid)

    def terminate_process(self, pid: int) -> bool:
        process = self.get_process(pid)
        if process:
            return process.terminate()
        return False

    def set_process_priority(self, pid: int, priority: int) -> bool:
        process = self.get_process(pid)
        if process:
            return process.set_priority(priority)
        return False
