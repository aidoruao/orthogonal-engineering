"""
Function Template for 1B LOC Fractal Architecture

This template defines how function nodes expand into actual Python code.

Standard: Yeshua
Version: 1.0.0
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
    
    # Generate docstring
    docstring = f"""
    Auto-generated function: {func_name}
    Batch: {batch}
    Module: {module}
    File: {file}
    Function Index: {node['index']}
    
    Part of 1B LOC Fractal Architecture
    Generated from seed (Yeshua Standard)
    Created: {seed.get('metadata', {}).get('created', 'unknown')}
    
    This function processes input data through deterministic transformations.
    Each line represents a specific processing step in the pipeline.
    """.strip()
    
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
    
    return content
