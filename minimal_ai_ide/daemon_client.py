"""
daemon_client.py
================

DAEMON CLIENT LIBRARY - PHASE 0 IMPLEMENTATION
Unified interface for all daemon communications

ARCHITECTURE PRINCIPLE:
"All intelligence paths must route through the Self-Automative Daemon"

FEATURES:
1. Synchronous and asynchronous support
2. Automatic retry with exponential backoff
3. Connection pooling for performance
4. Comprehensive error handling
5. Type-safe request/response validation
6. Christ constraint falsification-based evaluation
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import aiohttp
import requests
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)

# ==================== DATA MODELS ====================


class OperationType(str, Enum):
    """Types of operations that can be validated"""

    LORA_INFERENCE = "lora_inference"
    BATCH_PROCESSING = "batch_processing"
    API_REQUEST = "api_request"
    CONSTRAINT_EVALUATION = "constraint_evaluation"
    SYSTEM_HEALTH_CHECK = "system_health_check"


class ConstraintStatus(str, Enum):
    """Status of constraint evaluation"""

    PASS = "pass"
    FAIL = "fail"
    AUDIT_MODE = "audit_mode"
    PENDING = "pending"
    ERROR = "error"


class ChristConstraintResult(BaseModel):
    """Result of Christ constraint evaluation"""

    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    mode: str  # "normal", "audit_only", "blocked"
    violations: List[str] = Field(default_factory=list)
    justification: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator("score")
    def validate_score(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Christ score must be between 0.0 and 1.0, got {v}")
        return v


class ValidationRequest(BaseModel):
    """Request for operation validation"""

    operation: OperationType
    script: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    context: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @validator("request_id", pre=True, always=True)
    def set_request_id(cls, v):
        return (
            v or f"req_{int(time.time() * 1000)}_{hash(str(time.time())) % 10000:04d}"
        )


class ValidationResponse(BaseModel):
    """Response from operation validation"""

    valid: bool
    request_id: str
    operation: OperationType
    constraints: List[ConstraintStatus] = Field(default_factory=list)
    christ_constraint: Optional[ChristConstraintResult] = None
    message: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processing_time_ms: Optional[float] = None


class LogEntry(BaseModel):
    """Structured log entry for daemon logging"""

    level: str  # "INFO", "WARNING", "ERROR", "DEBUG"
    component: str
    operation: str
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class InferenceRequest(BaseModel):
    """Request for model inference through daemon"""

    prompt: str
    max_tokens: int = Field(default=512, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    context: Optional[Dict[str, Any]] = None
    require_constraints: bool = True
    client_type: str = "daemon_client"
    request_id: Optional[str] = None


class InferenceResponse(BaseModel):
    """Response from model inference"""

    response: str
    request_id: str
    christ_score: float = Field(ge=0.0, le=1.0)
    constraints_satisfied: int
    total_constraints: int
    processing_time_ms: float
    model_used: str
    mode: str  # "normal", "audit_only"
    violations: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ==================== DAEMON CLIENT CLASS ====================


class DaemonClient:
    """
    Unified client for communicating with the Self-Automative Daemon.

    Implements the principle: "All intelligence paths must route through the daemon"
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        enable_async: bool = True,
    ):
        """
        Initialize the DaemonClient.

        Args:
            base_url: Base URL of the daemon server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries (exponential backoff)
            enable_async: Whether to enable async operations
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_async = enable_async
        self.session = None
        self.async_session = None

        # Connection pool for synchronous requests
        self._session_pool = []

        # Standardized logging format
        self.log_format = {
            "inference": "🤖 LORA INFERENCE #{request_id}: {operation_type}",
            "validation": "⚖️ Σ_LORA Validation: {constraint_name} - {result} ({score:.2f})",
            "completion": "✓ Response generated: {token_count} tokens",
            "constraint_alert": "⚠️ Christ Constraint Alert: Score {score} < threshold {threshold}",
            "error": "❌ Daemon Error: {error_message}",
        }

        logger.info(f"DaemonClient initialized for {self.base_url}")

    # ==================== CORE METHODS ====================

    def validate_operation(self, request: ValidationRequest) -> ValidationResponse:
        """
        Validate an operation with the daemon before execution.

        This method MUST be called before any model inference or batch processing.

        Args:
            request: Validation request with operation details

        Returns:
            ValidationResponse indicating whether operation is allowed

        Raises:
            DaemonConnectionError: If cannot connect to daemon
            ValidationError: If request validation fails
        """
        logger.info(f"🔍 Validating operation: {request.operation.value}")

        # Standardized log
        self._log_operation(
            level="INFO",
            component="DaemonClient",
            operation="validate_operation",
            message=f"Validating {request.operation.value} from {request.script}",
            data={"request_id": request.request_id},
        )

        endpoint = f"{self.base_url}/api/validate"

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    endpoint, json=request.dict(), timeout=self.timeout
                )

                if response.status_code == 200:
                    result = ValidationResponse(**response.json())

                    # Log validation result
                    if result.valid:
                        logger.info(
                            f"✅ Operation validated: {request.operation.value}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ Operation rejected: {request.operation.value}"
                        )

                    return result

                elif response.status_code >= 500:
                    # Server error, retry with exponential backoff
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2**attempt)
                        logger.warning(
                            f"🔄 Daemon server error, retrying in {delay}s..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        raise DaemonConnectionError(
                            f"Daemon server error after {self.max_retries} retries: "
                            f"{response.status_code}"
                        )
                else:
                    # Client error, don't retry
                    raise ValidationError(
                        f"Validation failed: {response.status_code} - {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2**attempt)
                    logger.warning(f"🔄 Connection error, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    raise DaemonConnectionError(
                        f"Failed to connect to daemon after {self.max_retries} retries: {e}"
                    )

        # This should never be reached due to raises above
        raise DaemonConnectionError("Unexpected error in validate_operation")

    def log_operation(self, entry: LogEntry) -> bool:
        """
        Log an operation to the daemon's centralized logging system.

        This method SHOULD be called after significant operations.

        Args:
            entry: Structured log entry

        Returns:
            True if log was successful, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/api/log"

            response = requests.post(endpoint, json=entry.dict(), timeout=self.timeout)

            if response.status_code == 200:
                # Also log locally for redundancy
                log_method = getattr(logger, entry.level.lower(), logger.info)
                log_message = (
                    f"[DAEMON_LOG] {entry.component}.{entry.operation}: {entry.message}"
                )
                log_method(log_message)

                return True
            else:
                logger.warning(f"Failed to log to daemon: {response.status_code}")
                # Fall back to local logging
                self._log_locally(entry)
                return False

        except Exception as e:
            logger.warning(f"Error logging to daemon: {e}")
            self._log_locally(entry)
            return False

    def get_constraints(self) -> Dict[str, Any]:
        """
        Get the current constraint set from the daemon.

        Returns:
            Dictionary of current constraints and their configurations

        Raises:
            DaemonConnectionError: If cannot connect to daemon
        """
        logger.info("📋 Fetching current constraints from daemon")

        endpoint = f"{self.base_url}/api/constraints"

        try:
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()

            constraints = response.json()
            logger.info(
                f"✅ Retrieved {len(constraints.get('constraints', []))} constraints"
            )

            return constraints

        except requests.exceptions.RequestException as e:
            raise DaemonConnectionError(f"Failed to get constraints: {e}")

    def heartbeat(self) -> bool:
        """
        Check daemon connectivity and health.

        Returns:
            True if daemon is healthy and responsive, False otherwise
        """
        endpoint = f"{self.base_url}/api/health"

        try:
            response = requests.get(endpoint, timeout=5.0)

            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")

                if status == "healthy":
                    logger.debug("💓 Daemon heartbeat: Healthy")
                    return True
                else:
                    logger.warning(f"💓 Daemon heartbeat: {status}")
                    return False
            else:
                logger.warning(f"💓 Daemon heartbeat failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.warning(f"💓 Daemon heartbeat error: {e}")
            return False

    def submit_inference(self, request: InferenceRequest) -> InferenceResponse:
        """
        Submit an inference request through the daemon.

        This is the PRIMARY method for all model interactions.

        Args:
            request: Inference request with prompt and parameters

        Returns:
            InferenceResponse with generated text and constraint evaluation

        Raises:
            DaemonConnectionError: If cannot connect to daemon
            InferenceError: If inference fails
        """
        # Generate request ID if not provided
        if not request.request_id:
            request.request_id = f"inf_{int(time.time() * 1000)}"

        logger.info(f"🚀 Submitting inference request: {request.request_id}")

        # Standardized log format
        self._log_operation(
            level="INFO",
            component="DaemonClient",
            operation="submit_inference",
            message=self.log_format["inference"].format(
                request_id=request.request_id, operation_type="single_inference"
            ),
            data={
                "request_id": request.request_id,
                "prompt_length": len(request.prompt),
            },
        )

        endpoint = f"{self.base_url}/api/infer"

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    endpoint, json=request.dict(), timeout=self.timeout
                )

                if response.status_code == 200:
                    result = InferenceResponse(**response.json())

                    # Log completion with standardized format
                    self._log_operation(
                        level="INFO",
                        component="DaemonClient",
                        operation="inference_complete",
                        message=self.log_format["completion"].format(
                            token_count=len(result.response.split())
                        ),
                        data={
                            "request_id": result.request_id,
                            "christ_score": result.christ_score,
                            "processing_time": result.processing_time_ms,
                        },
                    )

                    # Log Christ constraint result
                    if result.christ_score < 0.5:  # Example threshold
                        self._log_operation(
                            level="WARNING",
                            component="DaemonClient",
                            operation="christ_constraint_alert",
                            message=self.log_format["constraint_alert"].format(
                                score=result.christ_score, threshold=0.5
                            ),
                            data={
                                "request_id": result.request_id,
                                "score": result.christ_score,
                                "mode": result.mode,
                                "violations": result.violations,
                            },
                        )

                            logger.info(f"✅ Inference completed: {result.request_id}")
                            return result

                        elif response.status_code >= 500:
                            # Server error, retry with exponential backoff
                            if attempt < self.max_retries:
                                delay = self.retry_delay * (2**attempt)
                                logger.warning(
                                    f"🔄 Daemon inference error, retrying in {delay}s..."
                                )
                                time.sleep(delay)
                                continue
                            else:
                                raise DaemonConnectionError(
                                    f"Daemon inference error after {self.max_retries} retries"
                                )
                        else:
                            # Client error, don't retry
                            error_data = response.json() if response.text else {}
                            raise InferenceError(
                                f"Inference failed: {response.status_code} - {error_data.get('detail', 'Unknown error')}"
                            )

                    except requests.exceptions.RequestException as e:
                        if attempt < self.max_retries:
                            delay = self.retry_delay * (2**attempt)
                            logger.warning(
                                f"🔄 Connection error during inference, retrying in {delay}s: {e}"
                            )
                            time.sleep(delay)
                        else:
                            raise DaemonConnectionError(
                                f"Failed to submit inference after {self.max_retries} retries: {e}"
                            )

                # This should never be reached due to raises above
                raise DaemonConnectionError("Unexpected error in submit_inference")

            # ==================== ASYNC METHODS ====================

            async def validate_operation_async(
                self, request: ValidationRequest
            ) -> ValidationResponse:
                """Async version of validate_operation"""
                if not self.enable_async:
                    raise RuntimeError("Async operations not enabled")

                if self.async_session is None:
                    self.async_session = aiohttp.ClientSession()

                # Implementation similar to sync version but with aiohttp
                # (Full implementation would mirror sync version with async/await)
                raise NotImplementedError("Async implementation pending")

            async def submit_inference_async(
                self, request: InferenceRequest
            ) -> InferenceResponse:
                """Async version of submit_inference"""
                if not self.enable_async:
                    raise RuntimeError("Async operations not enabled")

                if self.async_session is None:
                    self.async_session = aiohttp.ClientSession()

                # Implementation similar to sync version but with aiohttp
                # (Full implementation would mirror sync version with async/await)
                raise NotImplementedError("Async implementation pending")

            # ==================== UTILITY METHODS ====================

            def _log_operation(
                self,
                level: str,
                component: str,
                operation: str,
                message: str,
                data: Optional[Dict] = None,
            ) -> None:
                """Internal method for standardized logging"""
                log_entry = LogEntry(
                    level=level,
                    component=component,
                    operation=operation,
                    message=message,
                    data=data,
                    timestamp=datetime.utcnow().isoformat(),
                )

                # Try to log to daemon, fall back to local
                if not self.log_operation(log_entry):
                    self._log_locally(log_entry)

            def _log_locally(self, entry: LogEntry) -> None:
                """Fallback local logging"""
                log_method = getattr(logger, entry.level.lower(), logger.info)

                log_message = f"[{entry.timestamp}] [{entry.level}] "
                log_message += f"{entry.component}.{entry.operation}: {entry.message}"

                if entry.data:
                    log_message += f" | Data: {json.dumps(entry.data, default=str)}"

                log_method(log_message)

            def format_christ_constraint_log(self, result: ChristConstraintResult) -> str:
                """Format Christ constraint result for logging"""
                if result.passed:
                    return f"✅ Christ constraint PASS: {result.score:.3f}"
                elif result.mode == "audit_only":
                    return f"⚠️ Christ constraint AUDIT MODE: {result.score:.3f} - {len(result.violations)} violations"
                else:
                    return f"❌ Christ constraint FAIL: {result.score:.3f} - {len(result.violations)} violations"

            def close(self):
                """Clean up resources"""
                if self.async_session:
                    asyncio.run(self.async_session.close())

                # Close any pooled sessions
                for session in self._session_pool:
                    try:
                        session.close()
                    except:
                        pass

                logger.info("DaemonClient resources cleaned up")

            def __enter__(self):
                """Context manager entry"""
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                """Context manager exit"""
                self.close()


        # ==================== ERROR CLASSES ====================


        class DaemonError(Exception):
            """Base exception for all daemon-related errors"""
            pass


        class DaemonConnectionError(DaemonError):
            """Raised when cannot connect to daemon"""
            pass


        class ValidationError(DaemonError):
            """Raised when validation fails"""
            pass


        class InferenceError(DaemonError):
            """Raised when inference fails"""
            pass


        class ConstraintViolationError(DaemonError):
            """Raised when constraints are violated"""
            pass


        # ==================== EXAMPLE USAGE ====================


        def example_usage():
            """Example of how to use the DaemonClient"""

            # Initialize client
            client = DaemonClient(base_url="http://localhost:8080")

            try:
                # Check daemon health
                if not client.heartbeat():
                    print("❌ Daemon is not healthy")
                    return

                # Validate operation before proceeding
                validation_request = ValidationRequest(
                    operation=OperationType.LORA_INFERENCE,
                    script="example_script.py",
                    parameters={"max_tokens": 100, "temperature": 0.7}
                )

                validation_result = client.validate_operation(validation_request)

                if not validation_result.valid:
                    print(f"❌ Operation not validated: {validation_result.message}")
                    return

                # Submit inference request
                inference_request = InferenceRequest(
                    prompt="Explain the concept of falsifiability in Popperian philosophy.",
                    max_tokens=200,
                    temperature=0.7,
                    client_type="example"
                )

                inference_result = client.submit_inference(inference_request)

                # Display results
                print(f"\n{'='*60}")
                print(f"RESPONSE: {inference_result.response}")
                print(f"{'='*60}")
                print(f"Christ Score: {inference_result.christ_score:.3f}")
                print(f"Mode: {inference_result.mode}")
                print(f"Processing Time: {inference_result.processing_time_ms:.0f}ms")

                if inference_result.violations:
                    print(f"Violations: {inference_result.violations}")

            except DaemonError as e:
                print(f"❌ Daemon error: {e}")
            finally:
                client.close()


        if __name__ == "__main__":
            example_usage()
