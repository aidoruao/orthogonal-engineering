"""
RepoDiagnoser — clone and analyse any public Git repository.

Reuses existing toolkit primitives:
- toolkit/oe/hasher.py   — hash_file(), hash_bytes_chunked()
- toolkit/oe/merkle.py   — MerkleTree
- minimal_ai_ide/repository_scanner.py — RepositoryScanner
"""

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional

from toolkit.oe.hasher import hash_file
from toolkit.oe.merkle import MerkleTree
from minimal_ai_ide.repository_scanner import RepositoryScanner

logger = logging.getLogger(__name__)


class RepoDiagnoser:
    """Clone and analyse a public Git repository.

    Parameters
    ----------
    clone_dir:
        Base directory for cloned repositories.
        Defaults to ``/tmp/repo_analysis``.
    """

    def __init__(self, clone_dir: str = "/tmp/repo_analysis") -> None:
        self.clone_dir = Path(clone_dir)
        self.clone_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Clone
    # ------------------------------------------------------------------

    def clone_repo(
        self,
        repo_url: str,
        depth: int = 1,
        ref: Optional[str] = None,
    ) -> Path:
        """Clone a public repository.

        Parameters
        ----------
        repo_url:
            HTTPS or SSH URL of the repository.
        depth:
            Shallow-clone depth.  Pass ``0`` for a full clone (required
            when checking out specific commits).
        ref:
            Branch or tag to check out.  ``None`` means the default branch.

        Returns
        -------
        Path
            Local path to the cloned repository root.
        """
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        target = self.clone_dir / repo_name

        if target.exists():
            logger.info("Removing existing clone at %s", target)
            shutil.rmtree(target)

        cmd = ["git", "clone"]
        if depth > 0:
            cmd += ["--depth", str(depth)]
        if ref:
            cmd += ["--branch", ref]
        cmd += [repo_url, str(target)]

        logger.info("Cloning %s → %s", repo_url, target)
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"git clone failed for {repo_url}: {exc.stderr.strip()}"
            ) from exc

        return target

    # ------------------------------------------------------------------
    # Analyse
    # ------------------------------------------------------------------

    def analyze(self, repo_path: Path) -> Dict:
        """Analyse a local repository.

        Uses :class:`~minimal_ai_ide.repository_scanner.RepositoryScanner`
        for structural scanning, ``toolkit.oe.hasher.hash_file`` for file
        hashing, and :class:`~toolkit.oe.merkle.MerkleTree` for fingerprint
        generation.

        Parameters
        ----------
        repo_path:
            Root of the repository to analyse.

        Returns
        -------
        dict with keys:
            ``scan``        — full RepositoryScanner result dict  
            ``file_hashes`` — mapping ``{relative_path: sha256_hex}``  
            ``merkle_root`` — hex root hash of the Merkle tree  
            ``tree``        — :class:`~toolkit.oe.merkle.MerkleTree` instance
                             (can be used to generate per-file inclusion proofs)
        """
        repo_path = Path(repo_path)

        # -- structural scan --------------------------------------------------
        logger.info("Running RepositoryScanner on %s", repo_path)
        scanner = RepositoryScanner(root_dir=str(repo_path))
        scan_results = scanner.scan_entire_repository()

        # -- hash every file + build Merkle tree ------------------------------
        tree = MerkleTree()
        file_hashes: Dict[str, str] = {}

        for filepath in sorted(repo_path.rglob("*")):
            if not filepath.is_file():
                continue
            if ".git" in filepath.parts:
                continue
            rel = str(filepath.relative_to(repo_path))
            try:
                h = hash_file(filepath)
            except OSError as exc:
                logger.warning("Skipping unreadable file %s: %s", rel, exc)
                continue
            file_hashes[rel] = h
            tree.add_leaf(rel, h)

        merkle_root = tree.build()
        logger.info(
            "Merkle root for %s: %s (%d files)", repo_path.name, merkle_root, len(file_hashes)
        )

        return {
            "scan": scan_results,
            "file_hashes": file_hashes,
            "merkle_root": merkle_root,
            "tree": tree,
        }

    # ------------------------------------------------------------------
    # Convenience: clone + analyse in one call
    # ------------------------------------------------------------------

    def diagnose(
        self,
        repo_url: str,
        depth: int = 1,
        ref: Optional[str] = None,
    ) -> Dict:
        """Clone *repo_url* and return :meth:`analyze` results.

        Parameters
        ----------
        repo_url:
            Public repository URL.
        depth:
            Shallow-clone depth (0 = full clone).
        ref:
            Branch or tag name (optional).

        Returns
        -------
        Same dict as :meth:`analyze`, with an additional ``"repo_path"`` key.
        """
        repo_path = self.clone_repo(repo_url, depth=depth, ref=ref)
        result = self.analyze(repo_path)
        result["repo_path"] = str(repo_path)
        return result
