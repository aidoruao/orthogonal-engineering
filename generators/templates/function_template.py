"""
Function Template for 1B LOC Fractal Architecture

This template defines how function nodes expand into actual Python code.
Supports recursive expansion and topological collapse.

Standard: Yeshua
Version: 2.0.0 (PR #23)
"""

FUNCTION_TEMPLATE = """
def {function_name}(input_data):
    \"\"\"
    {docstring}
    \"\"\"
    # Initialize result container
    result = []
    
    # Process input data through deterministic transformations
{processing_lines}
    
    # Return aggregated result
    return result
"""

# Template for recursive sub-universe expansion annotation
SUB_UNIVERSE_ANNOTATION = """
# === SUB-UNIVERSE EXPANSION POINT ===
# This node can spawn a recursive sub-universe at layer {next_layer}
# Sub-DAG Hash: {sub_dag_hash}
# Topological Collapse: {collapse_status}
# Sub-seed: {sub_seed}
# ====================================
"""


def expand_function(node, seed, children):
    """
    Generate function content from template.
    
    Args:
        node: DAGNode representing this function
        seed: Seed definition dictionary
        children: List of child node IDs
        
    Returns:
        String containing generated Python function code
    """
    import hashlib
    
    # Extract context from node ID
    parts = node['id'].split('/')
    batch = parts[1] if len(parts) > 1 else "unknown"
    module = parts[2] if len(parts) > 2 else "unknown"
    file = parts[3] if len(parts) > 3 else "unknown"
    func_name = parts[4] if len(parts) > 4 else f"func_{node['index']:06d}"
    
    # Check if this node is a sub-universe spawn point
    layer_index = node.get('layer_index', 0)
    sub_dag_hash = node.get('sub_dag_hash')
    sub_seed = node.get('sub_seed', 'N/A')
    is_spawn_point = sub_dag_hash is not None
    
    # Topological collapse check
    collapse_enabled = seed.get('topological_collapse', {}).get('enabled', False)
    collapse_status = "enabled" if collapse_enabled else "disabled"
    
    # Generate docstring
    docstring_parts = [
        f"Auto-generated function: {func_name}",
        f"Batch: {batch}",
        f"Module: {module}",
        f"File: {file}",
        f"Function Index: {node['index']}",
        f"Layer: {layer_index}",
        "",
        "Part of 1B LOC Fractal Architecture",
        "Generated from seed (Yeshua Standard)",
        f"Created: {seed.get('metadata', {}).get('created', 'unknown')}",
        "",
        "This function processes input data through deterministic transformations.",
        "Each line represents a specific processing step in the pipeline."
    ]
    
    # Add recursive expansion annotation if this is a spawn point
    if is_spawn_point:
        docstring_parts.extend([
            "",
            "=== RECURSIVE EXPANSION POINT ===",
            f"Can spawn sub-universe at layer {layer_index + 1}",
            f"Sub-DAG hash: {sub_dag_hash[:16]}..." if sub_dag_hash else "N/A",
            f"Topological collapse: {collapse_status}",
            "================================="
        ])
    
    docstring = "\n    ".join(docstring_parts).strip()
    
    # Generate processing lines using children
    lines = []
    seed_value = seed.get('generation', {}).get('seed_value', 42)
    
    for i, child_id in enumerate(children):
        # Deterministic data value based on child_id and seed
        combined = f"{child_id}_{seed_value}"
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        data_value = int(hash_obj.hexdigest()[:8], 16)
        
        line = f"    result.append(process_value({data_value}))  # {child_id.split('/')[-1]}"
        lines.append(line)
    
    # Fill template
    content = FUNCTION_TEMPLATE.format(
        function_name=func_name.replace('-', '_'),
        docstring=docstring,
        processing_lines='\n'.join(lines) if lines else '    pass  # No processing lines'
    )
    
    # Add sub-universe annotation if this is a spawn point
    if is_spawn_point:
        annotation = SUB_UNIVERSE_ANNOTATION.format(
            next_layer=layer_index + 1,
            sub_dag_hash=sub_dag_hash[:16] + "..." if sub_dag_hash else "N/A",
            collapse_status=collapse_status,
            sub_seed=sub_seed[:16] + "..." if isinstance(sub_seed, str) else "N/A"
        )
        content = annotation + content
    
    return content

