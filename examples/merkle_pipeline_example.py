"""
Example: Basic usage of the Merkle-rooted pipeline.

This example demonstrates how to:
1. Generate a manifest for a directory
2. Build a Merkle tree
3. Verify inclusion proofs
"""

from pathlib import Path
from toolkit.oe.manifest import ManifestGenerator
from toolkit.oe.merkle import build_merkle_tree_from_files, verify_inclusion_proof
from toolkit.oe.logger import PipelineLogger


def main():
    # Set up paths
    repo_path = Path('.')
    output_dir = Path('output')
    output_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = PipelineLogger(Path('logs/example_pipeline.jsonl'))
    
    # Step 1: Generate manifest
    print("Step 1: Generating manifest...")
    logger.log_start('generate_manifest', repo=str(repo_path))
    
    manifest_path = output_dir / 'manifest.jsonl'
    generator = ManifestGenerator(manifest_path)
    
    # Exclude common patterns
    exclude_patterns = [
        '.git/*',
        '*.pyc',
        '__pycache__/*',
        'node_modules/*',
    ]
    
    count = 0
    file_hashes = []
    
    for entry in generator.process_directory(repo_path, exclude_patterns):
        count += 1
        file_hashes.append((entry['path'], entry['hash']))
        
        if count % 100 == 0:
            print(f"  Processed {count} files...")
    
    generator.finalize()
    print(f"  Total files indexed: {count}")
    logger.log_complete('generate_manifest', files=count)
    
    # Step 2: Build Merkle tree
    print("\nStep 2: Building Merkle tree...")
    logger.log_start('build_merkle', files=count)
    
    tree = build_merkle_tree_from_files(file_hashes)
    print(f"  Merkle root: {tree.root}")
    
    # Save root
    root_file = output_dir / 'merkle_root.txt'
    root_file.write_text(tree.root)
    
    # Export proofs
    proofs_file = output_dir / 'merkle_proofs.jsonl'
    tree.export_proofs_jsonl(proofs_file)
    print(f"  Proofs saved to: {proofs_file}")
    
    logger.log_complete('build_merkle', root=tree.root)
    
    # Step 3: Verify a proof
    print("\nStep 3: Verifying inclusion proofs...")
    logger.log_start('verify_proofs')
    
    if file_hashes:
        # Get proof for first file
        first_path = file_hashes[0][0]
        proof = tree.get_inclusion_proof(first_path)
        
        # Verify it
        is_valid = verify_inclusion_proof(proof)
        print(f"  Proof for '{first_path}': {'VALID' if is_valid else 'INVALID'}")
        
        logger.log_complete('verify_proofs', verified=1, valid=is_valid)
    
    print("\nDone! Files created:")
    print(f"  - {manifest_path}")
    print(f"  - {root_file}")
    print(f"  - {proofs_file}")


if __name__ == '__main__':
    main()
