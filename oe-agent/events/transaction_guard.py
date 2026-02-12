#!/usr/bin/env python3
"""
OE-AGENT TRANSACTION GUARD
Context manager for atomic transaction lifecycle enforcement

Version: 1.0.0
Schema ID: TRANSACTION-GUARD-ATOMIC-1.0
Date: 2026-01-25

🎯 PURPOSE:
Enforce atomic transaction lifecycle with context manager pattern.
Guarantees that transactions are ALWAYS cleaned up (COMMIT or ABORT).

🔒 ATOMIC GUARANTEES:
1. No open transactions: Transaction always closed on context exit
2. No intent without resolution: INTENT always followed by COMMIT or ABORT
3. No state leaks: Transaction state cannot survive step execution
4. Uniform boundaries: All actions use same transaction pattern

🔗 CONTEXT MANAGER PATTERN:
with TransactionGuard(event_sink, xact_id) as tx:
    tx.write_intent(...)
    # Execute action
    tx.commit(...)  # or tx.abort(...) on failure
# Transaction ALWAYS closed here
"""

from typing import Any, Dict

from .event_sink import AtomicEventSink


class TransactionGuardError(Exception):
    """Base exception for transaction guard errors."""

    pass


class TransactionIntentNotWrittenError(TransactionGuardError):
    """Raised when commit is attempted without intent."""

    pass


class TransactionAlreadyResolvedError(TransactionGuardError):
    """Raised when attempting to resolve already-closed transaction."""

    pass


class TransactionGuard:
    """
    Context manager for atomic transaction lifecycle enforcement.

    Enforces the invariant: If begin_xact() happened, exit ALWAYS resolves it.
    """

    def __init__(self, event_sink: AtomicEventSink, xact_id: str):
        """
        Initialize transaction guard.

        Args:
            event_sink: Atomic event sink for logging
            xact_id: Unique transaction ID
        """
        self.event_sink = event_sink
        self.xact_id = xact_id
        self.intent_written = False
        self.resolved = False

    def __enter__(self):
        """
        Enter transaction context.

        Returns:
            self: TransactionGuard instance
        """
        self.event_sink.begin_xact(self.xact_id)
        return self

    def write_intent(self, **payload: Dict[str, Any]) -> str:
        """
        Write INTENT event for this transaction.

        Args:
            **payload: Intent payload parameters

        Returns:
            str: Event hash

        Raises:
            TransactionAlreadyResolvedError: If transaction already resolved
        """
        if self.resolved:
            raise TransactionAlreadyResolvedError(
                f"Cannot write intent for already-resolved transaction: {self.xact_id}"
            )

        self.intent_written = True
        return self.event_sink.write_intent(self.xact_id, **payload)

    def commit(self, **effect: Dict[str, Any]) -> str:
        """
        Write COMMIT event for this transaction.

        Args:
            **effect: Commit effect parameters

        Returns:
            str: Event hash

        Raises:
            TransactionIntentNotWrittenError: If intent not written
            TransactionAlreadyResolvedError: If transaction already resolved
        """
        if not self.intent_written:
            raise TransactionIntentNotWrittenError(
                f"Cannot commit without intent: {self.xact_id}"
            )
        if self.resolved:
            raise TransactionAlreadyResolvedError(
                f"Cannot commit already-resolved transaction: {self.xact_id}"
            )

        self.resolved = True
        return self.event_sink.write_commit(self.xact_id, **effect)

    def abort(
        self,
        step_id: int,
        plan_id: str,
        reason_code: str = "UNCAUGHT_EXCEPTION",
        **error_details: Dict[str, Any],
    ) -> str:
        """
        Write ABORT event for this transaction.

        Args:
            step_id: Step number in plan
            plan_id: Plan ID
            reason_code: Abort reason code
            **error_details: Error details

        Returns:
            str: Event hash

        Raises:
            TransactionAlreadyResolvedError: If transaction already resolved
        """
        if self.resolved:
            raise TransactionAlreadyResolvedError(
                f"Cannot abort already-resolved transaction: {self.xact_id}"
            )

        self.resolved = True
        return self.event_sink.write_abort(
            self.xact_id, step_id, plan_id, reason_code=reason_code, **error_details
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit transaction context.

        Ensures transaction is ALWAYS resolved (COMMIT or ABORT).

        Args:
            exc_type: Exception type if raised
            exc_val: Exception value if raised
            exc_tb: Exception traceback if raised

        Returns:
            bool: False to re-raise exception, True to suppress
        """
        try:
            # If exception occurred and intent was written but not resolved, abort
            if exc_val is not None and self.intent_written and not self.resolved:
                self.abort(
                    step_id=0,  # Default step ID for uncaught exceptions
                    plan_id="unknown_plan",
                    reason_code="UNCAUGHT_EXCEPTION",
                    error_details={
                        "exception_type": str(exc_type.__name__)
                        if exc_type
                        else "Unknown",
                        "exception_message": str(exc_val),
                        "transaction_id": self.xact_id,
                    },
                )
            # If no exception but intent was written and not resolved, this is an error
            elif exc_val is None and self.intent_written and not self.resolved:
                # This should never happen - intent written but no commit/abort
                # Force abort to prevent transaction leak
                self.abort(
                    step_id=0,
                    plan_id="unknown_plan",
                    reason_code="MISSING_RESOLUTION",
                    error_details={
                        "transaction_id": self.xact_id,
                        "description": "Intent written but transaction not resolved before context exit",
                    },
                )
            # If no intent written, just clean up the transaction
            elif not self.intent_written:
                # No intent means no need for explicit resolution
                # But we still need to clear the transaction state
                # Clear transaction state in event sink
                with self.event_sink._lock:
                    if self.event_sink._current_xact_id == self.xact_id:
                        self.event_sink._current_xact_id = None
                        self.event_sink._xact_intent_hash = None
        except Exception as cleanup_error:
            # If cleanup fails, log but don't mask original error
            print(
                f"Warning: Transaction cleanup failed for {self.xact_id}: {cleanup_error}"
            )

        # Always re-raise original exception if there was one
        return False
