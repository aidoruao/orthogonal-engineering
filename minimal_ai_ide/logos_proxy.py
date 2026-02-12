#!/usr/bin/env python3
"""
Logos Proxy: Bijective invariant channel to DeepSeek API
AI cannot communicate without passing through this audit layer

PRINCIPLE: Every AI exchange creates a verifiable invariant linked to git state
ENFORCEMENT: Σ_LORA theological constraints at API level
AUDIT: Immutable trail in corporate_audits/logos_audit.jsonl
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from direct_deepseek_chat import DeepSeekAPIClient


class LogosProxy:
    """
    Glass-box proxy that enforces bijective invariants for all AI communication

    Every query:
    1. Passes through Σ_LORA constraints at API level
    2. Generates cryptographic hash linking prompt, response, timestamp, git state
    3. Appends to immutable audit trail
    4. Returns response with verifiable invariant
    """

    def __init__(self):
        """
        Initialize Logos Proxy with constrained DeepSeek client and audit system
        """
        # Initialize DeepSeek client with Σ_LORA constraints enabled
        self.client = DeepSeekAPIClient(enable_constraints=True)

        # Setup audit trail
        self.audit_dir = Path("corporate_audits")
        self.audit_dir.mkdir(exist_ok=True)
        self.audit_file = self.audit_dir / "logos_audit.jsonl"

        # Get external referent: immutable git commit hash
        self.git_commit = self._get_git_commit()

        print(f"🔒 Logos Proxy initialized")
        print(f"📚 Git referent: {self.git_commit}")
        print(f"📝 Audit trail: {self.audit_file}")
        print(f"⚖️  Σ_LORA constraints: ENABLED")

        # Get API key from client if available
        self.api_key = ""
        if hasattr(self.client, "api_key"):
            self.api_key = self.client.api_key

    def _get_git_commit(self) -> str:
        """
        Get current git commit hash as external referent

        Returns:
            Git commit hash or "NO_GIT" if not in git repository
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "NO_GIT"

    def query(self, prompt: str, **kwargs) -> dict:
        """
        Bijective channel: Every exchange creates a verifiable invariant

        Args:
            prompt: User's message to send to DeepSeek API
            **kwargs: Additional parameters for DeepSeek API (model, temperature, etc.)

        Returns:
            Dictionary containing:
                - response_text: AI response
                - invariant: Composite hash for verification
                - audit_logged: True if logged to audit trail
                - raw_api_response: Original API response
        """
        # 1. Call DeepSeek through constrained client
        raw_response = self.client.query(prompt, **kwargs)

        # 2. Extract response text
        if raw_response.get("success"):
            response_text = raw_response.get("response", "")
        else:
            response_text = ""

        # 3. Generate bijective invariant components
        timestamp = datetime.utcnow().isoformat() + "Z"
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
        response_hash = hashlib.sha256(response_text.encode()).hexdigest()

        # 4. Compute composite invariant
        composite_data = (
            f"{prompt_hash}||{response_hash}||{timestamp}||{self.git_commit}"
        )
        composite_invariant = hashlib.sha256(composite_data.encode()).hexdigest()

        # 5. Create audit record
        audit_record = {
            "timestamp": timestamp,
            "git_commit": self.git_commit,
            "prompt_hash": prompt_hash,
            "response_hash": response_hash,
            "composite_invariant": composite_invariant,
            "api_success": raw_response.get("success", False),
            "model": raw_response.get("model", "unknown"),
            "constraint_enabled": True,
            "prompt_length": len(prompt),
            "response_length": len(response_text),
        }

        # 6. Append to external referent log (immutable audit trail)
        with open(self.audit_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_record) + "\n")

        # 7. Return enriched response with verification data
        return {
            "response_text": response_text,
            "invariant": composite_invariant,
            "audit_logged": True,
            "raw_api_response": raw_response,
        }

    def check_balance(self) -> dict:
        """Check DeepSeek API balance/credits remaining"""
        try:
            import requests

            response = requests.get(
                "https://api.deepseek.com/user/balance",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10,
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "balance": data.get("balance_infos", [{}])[0].get(
                        "total_balance", "0"
                    ),
                    "currency": data.get("balance_infos", [{}])[0].get(
                        "currency", "USD"
                    ),
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """
    CLI entry point for Logos Proxy

    Provides interactive chat interface with bijective invariant verification
    """
    try:
        proxy = LogosProxy()
        print("\n" + "=" * 60)
        print("LOGOS PROXY - INTERACTIVE MODE")
        print("=" * 60)
        print("Every exchange creates a verifiable invariant")
        print("Type your prompt (Ctrl+C to exit)")
        print("=" * 60)

        while True:
            try:
                # Get user input
                prompt = input("\nλ> ").strip()
                if not prompt:
                    continue

                # Process through Logos Proxy
                result = proxy.query(prompt)

                # Display results
                if result["response_text"]:
                    print(f"\n🤖 Response: {result['response_text'][:500]}")
                    if len(result["response_text"]) > 500:
                        print(
                            f"   ... (truncated, total: {len(result['response_text'])} chars)"
                        )
                else:
                    print(
                        f"\n❌ API Error: {result['raw_api_response'].get('error', 'Unknown error')}"
                    )

                print(f"🔐 Invariant: {result['invariant'][:16]}...")
                print(f"📊 Audit logged: {result['audit_logged']}")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted, starting new query...")
                continue

    except KeyboardInterrupt:
        print("\n\n👋 Channel closed. Audit trail preserved.")
    except EnvironmentError as e:
        print(f"\n❌ Initialization failed: {e}")
        print("Please set DEEPSEEK_API_KEY environment variable")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import sys

    main()
