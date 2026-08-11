#!/usr/bin/env python3
"""
TSS Blockchain Timestamp — Bitcoin Testnet ($0)
Uses public testnet API to verify blockchain is reachable.
"""
import json
import urllib.request
import sys
from datetime import datetime

def get_testnet_tip():
    """Get latest Bitcoin testnet block hash via public API."""
    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "network": "testnet",
        "method": "public_api",
        "status": "UNKNOWN",
        "block_hash": None,
        "block_height": None,
        "api_reachable": False
    }

    apis = [
        "https://api.blockcypher.com/v1/btc/test3",
        "https://testnet.blockchain.info/latestblock",
        "https://api.bitcore.io/api/BTC/testnet/block/tip"
    ]

    for api in apis:
        try:
            req = urllib.request.Request(
                api,
                headers={"User-Agent": "TSS-Testnet-Verifier/1.0"}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode())
                result["api_reachable"] = True
                result["status"] = "TESTNET_REACHABLE"

                # Extract block info based on API format
                if "hash" in data:
                    result["block_hash"] = data["hash"]
                elif "block_hash" in data:
                    result["block_hash"] = data["block_hash"]

                if "height" in data:
                    result["block_height"] = data["height"]
                elif "block_index" in data:
                    result["block_height"] = data["block_index"]

                return result

        except Exception as e:
            result["status"] = f"API_FAIL: {str(e)}"
            continue

    return result

if __name__ == "__main__":
    result = get_testnet_tip()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["status"] == "TESTNET_REACHABLE" else 1)
