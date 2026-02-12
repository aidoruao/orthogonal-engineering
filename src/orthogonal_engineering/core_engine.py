from pathlib import Path
from .pipeline import run_full_audit

class CoreEngine:
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)

    def run(self, output: str):
        return run_full_audit(self.data_path, Path(output))
