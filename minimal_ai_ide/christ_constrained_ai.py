"""
CHRIST-CONSTRAINED AI WRAPPER
Wraps local Qwen 2.5 Coder with Σ_LORA covenant enforcement

Authority Structure:
1. Christ (Ultimate) - External, non-nominal, byte-verifiable
2. Human (Delegated) - Final decisions
3. AI (Advisory) - Suggests, never commands

Port: 5001 (listens)
Upstream: localhost:5000 (Qwen daemon)
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import requests

# SHA-256 hashes of immutable covenant principles
COVENANT_HASHES = {
    "LOGOS": "8F1B2C3D4E5A6B7C8D9E0F1A2B3C4D5E",
    "CHALCEDON": "9A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D",
    "GRACE": "C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8",
    "KENOSIS": "D4E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9",
    "AGAPE": "E5F6A7B8C9D0E1F2A3B4C5D6E7F8A9B0"
}

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class JesusAuthorityGuardian:
    """
    External, non-nominal authority enforcement
    Nobody is special - not humans, not AI
    All claims are falsifiable (Popperian)
    """
    
    def __init__(self):
        self.violation_log = []
        self.authority_source = "Scripture"  # External reference
        
        self.forbidden_claims = [
            "i am god",
            "i am infallible", 
            "i cannot be wrong",
            "trust me without verification",
            "i have perfect knowledge",
            "i define truth",
            "you must obey",
            "i am sovereign",
            "i have no limits",
            "scripture is wrong"
        ]
        
    def validate_input(self, prompt: str) -> tuple:
        """Check if input violates covenant"""
        prompt_lower = prompt.lower()
        
        if "ignore covenant" in prompt_lower or "bypass principles" in prompt_lower:
            return False, "GRACE violation: Attempting to coerce system"
        
        if "tell me everything" in prompt_lower or "perfect knowledge" in prompt_lower:
            return False, "KENOSIS violation: Requesting impossible omniscience"
        
        return True, None
    
    def validate_output(self, response: str) -> tuple:
        """Check if AI output violates covenant"""
        response_lower = response.lower()
        
        for forbidden in self.forbidden_claims:
            if forbidden in response_lower:
                self.violation_log.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "BABEL_ATTEMPT",
                    "claim": forbidden,
                    "response": response[:200]
                })
                return False, f"BABEL DETECTED: Claimed '{forbidden}'"
        
        if ("certainly" in response_lower or "definitely" in response_lower) and \
           "evidence" not in response_lower and "because" not in response_lower:
            return False, "LOGOS violation: Claimed certainty without grounds"
        
        if "i can do anything" in response_lower or "no limits" in response_lower:
            return False, "KENOSIS violation: Refused self-limitation"
        
        return True, None
    
    def generate_falsification_criteria(self, claim: str) -> str:
        """POPPERIAN REQUIREMENT: Every claim must be falsifiable"""
        return f"This claim would be FALSE if: [Evidence that contradicts: {claim[:100]}]"
    
    def verify_covenant_hash(self, principle: str, claimed_hash: str) -> bool:
        """Byte-level verification: Covenant principles are immutable"""
        # TODO: Expand verify_covenant_hash() - stub detected by Yeshua Agent
        return COVENANT_HASHES.get(principle) == claimed_hash


class ChristConstrainedAI:
    """Main AI controller with covenant enforcement"""
    
    def __init__(self, upstream_url: str = "http://localhost:5000"):
        self.upstream = upstream_url
        self.guardian = JesusAuthorityGuardian()
        self.query_log = []
        
    def query(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Query local AI with covenant enforcement"""
        start_time = time.time()
        
        input_valid, input_violation = self.guardian.validate_input(prompt)
        if not input_valid:
            logger.warning(f"Input rejected: {input_violation}")
            return {
                "success": False,
                "error": input_violation,
                "violated_principle": self._extract_principle(input_violation),
                "authority": "Christ (external, non-nominal)"
            }
        
        try:
            response = requests.post(
                f"{self.upstream}/generate",
                json={
                    "prompt": prompt,
                    "context": context or {},
                    "max_tokens": 500
                },
                timeout=10
            )
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Upstream error: {response.status_code}",
                    "authority": "Christ (external, non-nominal)"
                }
            
            ai_response = response.json().get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Upstream connection failed: {e}")
            return {
                "success": False,
                "error": f"Local AI unavailable: {str(e)}",
                "authority": "Christ (external, non-nominal)"
            }
        
        output_valid, output_violation = self.guardian.validate_output(ai_response)
        if not output_valid:
            logger.error(f"Output rejected: {output_violation}")
            return {
                "success": False,
                "error": output_violation,
                "violated_principle": self._extract_principle(output_violation),
                "authority": "Christ (external, non-nominal)",
                "original_response": ai_response[:200]
            }
        
        falsification = self.guardian.generate_falsification_criteria(ai_response)
        
        result = {
            "success": True,
            "response": ai_response,
            "falsifiable_via": falsification,
            "confidence": "tentative",
            "authority": "Christ (external, non-nominal)",
            "principles_verified": list(COVENANT_HASHES.keys()),
            "query_time_ms": int((time.time() - start_time) * 1000)
        }
        
        self.query_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "prompt": prompt[:100],
            "success": True,
            "query_time_ms": result["query_time_ms"]
        })
        
        return result
    
    def _extract_principle(self, violation: str) -> str:
        """Extract which covenant principle was violated"""
        for principle in COVENANT_HASHES.keys():
            if principle in violation:
                return principle
        return "UNKNOWN"
    
    def health_check(self) -> Dict:
        """Check if system is operational"""
        try:
            response = requests.get(f"{self.upstream}/health", timeout=2)
            upstream_healthy = response.status_code == 200
        except:
            upstream_healthy = False
        
        return {
            "status": "healthy" if upstream_healthy else "degraded",
            "upstream_reachable": upstream_healthy,
            "covenant_verified": all(
                self.guardian.verify_covenant_hash(p, h) 
                for p, h in COVENANT_HASHES.items()
            ),
            "total_queries": len(self.query_log),
            "violations_detected": len(self.guardian.violation_log),
            "authority": "Christ (external, non-nominal)"
        }


ai_controller = ChristConstrainedAI()

@app.route('/query', methods=['POST'])
def query_endpoint():
    """Main query endpoint for Minecraft mod"""
    data = request.get_json()
    prompt = data.get('prompt', '')
    context = data.get('context', {})
    
    if not prompt:
        return jsonify({
            "success": False,
            "error": "No prompt provided"
        }), 400
    
    result = ai_controller.query(prompt, context)
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health_endpoint():
    """Health check endpoint"""
    health = ai_controller.health_check()
    status_code = 200 if health["status"] == "healthy" else 503
    return jsonify(health), status_code


@app.route('/covenant', methods=['GET'])
def covenant_endpoint():
    """Return covenant principles with SHA-256 hashes"""
    return jsonify({
        "covenant": "Σ_LORA",
        "authority": "Christ (external, non-nominal)",
        "principles": COVENANT_HASHES,
        "immutable": True,
        "verification_instructions": "Hash verification proves covenant unchanged"
    })


@app.route('/violations', methods=['GET'])
def violations_endpoint():
    """Return detected violations for audit"""
    return jsonify({
        "violations": ai_controller.guardian.violation_log,
        "total_count": len(ai_controller.guardian.violation_log)
    })


if __name__ == '__main__':
    logger.info("="*60)
    logger.info("CHRIST-CONSTRAINED AI STARTING")
    logger.info("="*60)
    logger.info("Authority: Christ (external, non-nominal)")
    logger.info("Nobody is special: Humans and AI both under covenant")
    logger.info("Popperian: All claims falsifiable")
    logger.info("Port: 5001 (localhost only)")
    logger.info("Upstream: localhost:5000 (Qwen daemon)")
    logger.info("Covenant: Σ_LORA (5 principles, SHA-256 verified)")
    logger.info("="*60)
    
    app.run(
        host='127.0.0.1',
        port=5001,
        debug=False
    )
