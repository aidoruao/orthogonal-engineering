"""System Analyzer Agent - save as: system_analyzer_agent.py"""
# save as: system_analyzer_agent.py
import os
import ast
import json
import logging
import pandas as pd
from datetime import datetime

# LOGGING CONFIGURATION (UTF-8 file output, ASCII console)
logging.basicConfig(
    filename='pipeline_run_log.txt',
    level=logging.INFO,
    encoding='utf-8',
    format='%(asctime)s - %(message)s'
)

class FileSystemAI:
    """Local AI-like agent that analyzes files without external APIs"""
    
    def __init__(self, root_dir=None):
        self.root = root_dir or os.getcwd()
        self.analysis = {
            "timestamp": datetime.now().isoformat(),
            "root_directory": self.root,
            "file_stats": {},
            "code_insights": [],
            "data_insights": [],
            "recommendations": []
        }
    
    def analyze_directory(self):
        logging.info(f"SYSTEM AGENT ACTIVATED - Analyzing: {self.root}")
        print(f"\n[ANALYZING] {os.path.basename(self.root)}")
        print("=" * 60)
        
        for root, dirs, files in os.walk(self.root):
            level = root.replace(self.root, '').count(os.sep)
            indent = ' ' * 2 * level
            logging.info(f'{indent}[DIR] {os.path.basename(root)}/')
            
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                filepath = os.path.join(root, file)
                self._analyze_file(filepath)
                logging.info(f'{subindent}[FILE] {file}')
        
        self._generate_insights()
        self._print_report()
        
        report_file = f"system_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.analysis, f, indent=2)
        logging.info(f"Analysis saved to: {report_file}")
        print(f"\n[SUCCESS] Analysis complete. See pipeline_run_log.txt and {report_file}")
    
    def _analyze_file(self, filepath):
        ext = os.path.splitext(filepath)[1].lower()
        size = os.path.getsize(filepath)
        rel_path = os.path.relpath(filepath, self.root)
        
        stats = {
            "path": rel_path,
            "size_bytes": size,
            "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
            "type": ext[1:] if ext else "unknown"
        }
        
        if ext == '.py':
            stats.update(self._analyze_python(filepath))
        elif ext == '.csv':
            stats.update(self._analyze_csv(filepath))
        self.analysis["file_stats"][rel_path] = stats
    
    def _analyze_python(self, filepath):
        insights = {"functions": [], "classes": [], "imports": [], "lines": 0}
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                insights["lines"] = len(content.split('\n'))
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    insights["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    insights["classes"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        insights["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    insights["imports"].append(f"from {node.module}")
            if insights["functions"] or insights["classes"]:
                self.analysis["code_insights"].append({
                    "file": os.path.relpath(filepath, self.root),
                    "functions": len(insights["functions"]),
                    "classes": len(insights["classes"]),
                    "imports": len(insights["imports"])
                })
        except Exception as e:
            insights["error"] = str(e)
        return insights
    
    def _analyze_csv(self, filepath):
        insights = {"rows": 0, "columns": [], "dtypes": {}}
        try:
            df = pd.read_csv(filepath, nrows=1000)
            insights["rows"] = len(df)
            insights["columns"] = list(df.columns)
            insights["dtypes"] = {col: str(dtype) for col, dtype in df.dtypes.items()}
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                stats = df[numeric_cols].describe().to_dict()
                insights["numeric_stats"] = stats
            self.analysis["data_insights"].append({
                "file": os.path.relpath(filepath, self.root),
                "rows": insights["rows"],
                "columns": len(insights["columns"]),
                "has_numeric": len(numeric_cols) > 0
            })
        except Exception as e:
            insights["error"] = str(e)
        return insights
    
    def _generate_insights(self):
        if self.analysis["code_insights"]:
            total_funcs = sum(ci["functions"] for ci in self.analysis["code_insights"])
            total_classes = sum(ci["classes"] for ci in self.analysis["code_insights"])
            self.analysis["recommendations"].append(
                f"Codebase has {total_funcs} functions and {total_classes} classes across "
                f"{len(self.analysis['code_insights'])} Python files."
            )
        if self.analysis["data_insights"]:
            total_rows = sum(di["rows"] for di in self.analysis["data_insights"])
            self.analysis["recommendations"].append(
                f"Found {len(self.analysis['data_insights'])} CSV files with total ~{total_rows:,} rows."
            )
    
    def _print_report(self):
        logging.info("=" * 60)
        logging.info("AI AGENT ANALYSIS REPORT")
        logging.info("=" * 60)
        total_files = len(self.analysis["file_stats"])
        logging.info(f"SUMMARY: Files analyzed: {total_files}")
        
        extensions = {}
        for stats in self.analysis["file_stats"].values():
            ext = stats.get("type", "unknown")
            extensions[ext] = extensions.get(ext, 0) + 1
        for ext, count in sorted(extensions.items()):
            logging.info(f"  • .{ext}: {count} files")
            
        if self.analysis["code_insights"]:
            logging.info("CODE ANALYSIS:")
            for insight in self.analysis["code_insights"]:
                logging.info(f"  • {insight['file']}: {insight['functions']} funcs, {insight['classes']} classes")
                
        if self.analysis["data_insights"]:
            logging.info("DATA ANALYSIS:")
            for insight in self.analysis["data_insights"]:
                logging.info(f"  • {insight['file']}: {insight['rows']:,} rows, {insight['columns']} columns")
                
        if self.analysis["recommendations"]:
            logging.info("RECOMMENDATIONS:")
            for i, rec in enumerate(self.analysis["recommendations"], 1):
                logging.info(f"  {i}. {rec}")
                
        logging.info("Analysis complete. All processing done locally.")
        print(f"[REPORT] {total_files} files analyzed - See pipeline_run_log.txt for details")

def quick_analyze():
    agent = FileSystemAI()
    agent.analyze_directory()

if __name__ == "__main__":
    quick_analyze()
