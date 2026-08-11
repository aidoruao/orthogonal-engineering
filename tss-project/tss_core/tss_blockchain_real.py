import subprocess
import tempfile
import os

class RealIPFSReplicator:
    def replicate(self, data: bytes) -> str:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(data)
            tmp = f.name
        try:
            result = subprocess.run(
                ["ipfs", "add", "-q", tmp],
                capture_output=True, text=True, timeout=30
            )
            os.unlink(tmp)
            if result.returncode == 0:
                cid = result.stdout.strip()
                if len(cid) == 46 and cid.startswith("Qm"):
                    return cid
            return ""
        except Exception:
            return ""

if __name__ == "__main__":
    rep = RealIPFSReplicator()
    cid = rep.replicate(b"TSS v11 real test")
    valid = len(cid) == 46 and cid.startswith("Qm")
    print(f"CID: {cid}")
    print(f"VALID: {valid}")
