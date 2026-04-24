import ast

# ==========================================
# ROLE 2: ETL/ELT BUILDER
# ==========================================
# Task: Extract docstrings and comments from legacy Python code.

def extract_logic_from_code(file_path):
    # --- FILE READING (Handled for students) ---
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    
    logic_metadata = {
        "functions": [],
        "business_rules": []
    }
    
    try:
        tree = ast.parse(source_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                logic_metadata["functions"].append({
                    "name": node.name,
                    "docstring": docstring if docstring else "No docstring provided"
                })
    except SyntaxError:
        logic_metadata["functions"] = "Error parsing AST: Syntax Error"

    rule_pattern = r'#\s*(Business Logic Rule\s*\d+.*)'
    rules = re.findall(rule_pattern, source_code, re.IGNORECASE)
    logic_metadata["business_rules"] = [rule.strip() for rule in rules]
    
    return {
        "source_file": file_path,
        "content_type": "source_code_analysis",
        "extracted_logic": logic_metadata,
        "status": "success"
    }
    
    return {}

