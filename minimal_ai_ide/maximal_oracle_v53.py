"""Maximal Oracle V53 - -------------------------"""
import asyncio, aiohttp, ast, json, time, logging
from typing import Dict, List, Set
from prometheus_client import Counter, Histogram, start_http_server
from z3 import Solver, Bool, sat
import hashlib

# -------------------------
# CUSTOM VALIDATION EXCEPTIONS
# -------------------------
class ValidationError(Exception):
    pass

# -------------------------
# FILE MANAGEMENT & SNAPSHOTS (interval-based)
# -------------------------
class FileManager:
    def __init__(self, snapshot_interval: int = 10):
        self.files: Dict[str, str] = {}
        self.snapshots: List[Dict] = []
        self._crdt_nodes: Dict[str, "CRDTNode"] = {}
        self._token_counter = 0
        self.snapshot_interval = snapshot_interval  # snapshot every N validated tokens

    def read_file(self, file: str) -> str:
        return self.files.get(file, "")

    def write_file(self, file: str, content: str):
        self.files[file] = content

    async def snapshot(self) -> Dict:
        snap = {"hash": self._compute_hash(), "updates": self.files.copy()}
        self.snapshots.append(snap)
        return snap

    async def snapshot_if_needed(self):
        if self._token_counter % self.snapshot_interval == 0:
            await self.snapshot()

    async def get_last_valid_snapshot(self, file: str) -> str:
        for snap in reversed(self.snapshots):
            if file in snap["updates"]:
                return snap["updates"][file]
        return ""

    def _compute_hash(self) -> str:
        m = hashlib.sha256()
        for f, c in sorted(self.files.items()):
            m.update(f.encode())
            m.update(c.encode())
        return m.hexdigest()

# -------------------------
# CROSS-FILE INVARIANTS & AST
# -------------------------
class SymbolExtractor(ast.NodeVisitor):
    def __init__(self):
        self.defs: Set[str] = set()
        self.calls: Set[str] = set()
    def visit_FunctionDef(self, node):
        self.defs.add(node.name)
        self.generic_visit(node)
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        self.generic_visit(node)

class CrossFileInvariants:
    def __init__(self, fm: FileManager):
        self.fm = fm

    async def enforce(self) -> List[str]:
        """Return invalid files, do NOT raise exceptions"""
        invalid_files = []
        func_defs = {}
        for f, content in self.fm.files.items():
            try:
                tree = ast.parse(content)
                extractor = SymbolExtractor()
                extractor.visit(tree)
                func_defs[f] = extractor.defs
            except SyntaxError:
                continue
        for f, content in self.fm.files.items():
            try:
                tree = ast.parse(content)
                extractor = SymbolExtractor()
                extractor.visit(tree)
                for call in extractor.calls:
                    if not any(call in defs for defs in func_defs.values()):
                        invalid_files.append(f)
            except SyntaxError:
                continue
        return list(set(invalid_files))

# -------------------------
# CONTRACT VERIFICATION
# -------------------------
class ContractVerifier:
    def __init__(self, fm: FileManager):
        self.fm = fm
        self.solver = Solver()

    def encode_file_contracts(self, filename: str, content: str):
        try:
            tree = ast.parse(content)
            extractor = SymbolExtractor()
            extractor.visit(tree)
            for call in extractor.calls:
                if call not in extractor.defs:
                    var = Bool(f"{filename}_{call}_exists")
                    self.solver.add(var == False)
            for fn in extractor.defs:
                var = Bool(f"{filename}_{fn}_exists")
                self.solver.add(var == True)
        except SyntaxError:
            pass

    def verify(self) -> List[str]:
        failing_files = []
        if self.solver.check() == sat:
            model = self.solver.model()
            for d in model.decls():
                if str(model[d]) == "False":
                    fname = d.name().split("_")[0]
                    failing_files.append(fname)
        return list(set(failing_files))

# -------------------------
# TYPE ENFORCEMENT
# -------------------------
class TypeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.type_issues: List = []
    def visit_FunctionDef(self, node):
        if node.returns is None:
            self.type_issues.append((node.name, "Missing return type hint"))
        self.generic_visit(node)
    def visit_AnnAssign(self, node):
        if node.annotation is None:
            self.type_issues.append((node.target.id, "Missing variable type hint"))
        self.generic_visit(node)

class TypeEnforcer:
    def __init__(self, fm: FileManager):
        self.fm = fm

    async def enforce(self) -> Dict[str, list]:
        issues = {}
        for f, content in self.fm.files.items():
            try:
                tree = ast.parse(content)
                analyzer = TypeAnalyzer()
                analyzer.visit(tree)
                if analyzer.type_issues:
                    issues[f] = analyzer.type_issues
            except SyntaxError:
                continue
        return issues

# -------------------------
# CONFIDENCE PROPAGATION (interval-based)
# -------------------------
class ConfidencePropagator:
    def __init__(self, dag: dict, graph_widget):
        self.dag = dag
        self.graph_widget = graph_widget
        self._last_propagated = {}

    def propagate_if_needed(self, file: str, confidence: float):
        if self._last_propagated.get(file, 0) < time.time() - 0.2:
            self._propagate_recursive(file, confidence, set())
            self._last_propagated[file] = time.time()

    def _propagate_recursive(self, file: str, confidence: float, visited: set):
        if file in visited:
            return
        visited.add(file)
        self.graph_widget.update_confidence(file, confidence)
        for downstream in [f for f, deps in self.dag.items() if file in deps]:
            decay_conf = confidence * 0.9
            self._propagate_recursive(downstream, decay_conf, visited)

# -------------------------
# STREAMING + TOKEN BUFFER + RETRY PER TOKEN
# -------------------------
class DeepSeekStreamer:
    def __init__(self, api_key: str, endpoint: str, rate_limit: float = 0.1):
        self.api_key = api_key
        self.endpoint = endpoint
        self.rate_limit = rate_limit

    async def stream(self, prompt: str):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.endpoint,
                json={"prompt": prompt, "stream": True},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as resp:
                async for line in resp.content:
                    line = line.decode().strip()
                    if line.startswith("data: "):
                        token = json.loads(line[6:]).get("token", "")
                        await asyncio.sleep(self.rate_limit)
                        yield token

# -------------------------
# ROLLBACK CASCADE
# -------------------------
class RollbackCascade:
    def __init__(self, fm: FileManager, cross_file_validator: CrossFileInvariants):
        self.fm = fm
        self.validator = cross_file_validator
        self._rollback_lock = asyncio.Lock()

    async def validate_and_rollback(self, file: str) -> bool:
        """Return True if rollback occurred, False otherwise"""
        async with self._rollback_lock:
            invalid_files = await self.validator.enforce()
            if file in invalid_files:
                prev_content = await self.fm.get_last_valid_snapshot(file)
                self.fm.write_file(file, prev_content)
                return True
            return False

# -------------------------
# CRDT MANAGER
# -------------------------
class CRDTNode:
    def __init__(self, content: str):
        self.content = content
        self.timestamp = asyncio.get_event_loop().time()

class CRDTManager:
    def __init__(self, fm: FileManager):
        self.fm = fm

    async def merge_if_valid(self, file: str, candidate: str, timestamp: float = None):
        if timestamp is None:
            timestamp = asyncio.get_event_loop().time()
        node = getattr(self.fm, f"_crdt_{file}", CRDTNode(self.fm.read_file(file)))
        if timestamp >= node.timestamp:
            node.content = candidate
            node.timestamp = timestamp
        setattr(self.fm, f"_crdt_{file}", node)

# -------------------------
# MONITORING + LOGGING
# -------------------------
AI_REQUESTS = Counter("ai_requests_total", "Total AI requests")
AI_LATENCY = Histogram("ai_request_latency_seconds", "Latency of AI requests")

class Monitoring:
    def __init__(self, port: int = 8000):
        start_http_server(port)
    def log_request(self, latency: float):
        AI_REQUESTS.inc()
        AI_LATENCY.observe(latency)

class EnterpriseLogger:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("OracleIDE")
    def log_token(self, file: str, token: str, user_id: str):
        # TODO: Expand log_token() - stub detected by Yeshua Agent
        self.logger.info(f"[{user_id}] Token in {file}: {token}")

class EnterpriseHooks:
    def __init__(self, monitor: Monitoring, logger: EnterpriseLogger):
        self.monitor = monitor
        self.logger = logger
    async def handle_token(self, file: str, token: str, user_id: str, latency: float):
        self.logger.log_token(file, token, user_id)
        self.monitor.log_request(latency)

# -------------------------
# ORACLE IDE CONTROLLER V53
# -------------------------
class OracleIDEController:
    def __init__(self, api_key: str, endpoint: str, dag: dict, graph_widget, max_retries: int = 5):
        self.fm = FileManager(snapshot_interval=20)  # snapshot every 20 validated tokens
        self.cross_file_validator = CrossFileInvariants(self.fm)
        self.contract_verifier = ContractVerifier(self.fm)
        self.type_enforcer = TypeEnforcer(self.fm)
        self.confidence_propagator = ConfidencePropagator(dag, graph_widget)
        self.streamer = DeepSeekStreamer(api_key, endpoint)
        self.rollback_cascade = RollbackCascade(self.fm, self.cross_file_validator)
        self.crdt = CRDTManager(self.fm)
        self.enterprise_logger = EnterpriseLogger()
        self.monitoring = Monitoring()
        self.hooks = EnterpriseHooks(self.monitoring, self.enterprise_logger)
        self.graph_widget = graph_widget
        self.max_retries = max_retries

    async def _is_syntactic_boundary(self, token: str) -> bool:
        return token in {"\n", ")", ":", ";"}  # basic heuristics

    async def _validate_all(self, file: str, candidate: str):
        """Validate invariants, type, and contract before CRDT merge"""
        invalid_files = await self.cross_file_validator.enforce()
        if file in invalid_files:
            raise ValidationError(f"Cross-file invariant failed for {file}")
        type_issues = await self.type_enforcer.enforce()
        if file in type_issues:
            raise ValidationError(f"Type issues in {file}: {type_issues[file]}")
        self.contract_verifier.encode_file_contracts(file, candidate)
        failing_contracts = self.contract_verifier.verify()
        if file in failing_contracts:
            raise ValidationError(f"Contract violations in {file}")

    async def handle_user_stream(self, file: str, prompt: str, user_id: str):
        """Token-level streaming with per-token retry, interval snapshots, syntactic-boundary validation"""
        buffer = []
        token_gen = self.streamer.stream(prompt)
        async for token in token_gen:
            buffer.append(token)
            candidate = self.fm.read_file(file) + token
            if await self._is_syntactic_boundary(token):
                for attempt in range(self.max_retries):
                    try:
                        # validate BEFORE merge
                        await self._validate_all(file, candidate)
                        await self.crdt.merge_if_valid(file, candidate)
                        # Snapshot only on validated content
                        await self.fm.snapshot_if_needed()
                        break  # successful validation for this token
                    except ValidationError as e:
                        buffer.pop()  # remove failed token
                        # Transform token (example: drop token, can add correction logic)
                        candidate = self.fm.read_file(file)
                        if attempt == self.max_retries - 1:
                            self.enterprise_logger.logger.warning(f"Token dropped after {self.max_retries} retries: {token}")
            # propagate confidence intermittently
            self.confidence_propagator.propagate_if_needed(file, 0.9)
            # logging + monitoring
            latency = 0.01  # placeholder
            await self.hooks.handle_token(file, token, user_id, latency)
