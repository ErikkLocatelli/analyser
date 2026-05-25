import javalang
from pathlib import Path

def calculate_complexity(node) -> int:
    """Conta if/else-if recursivamente na AST."""
    count = 0
    if isinstance(node, (javalang.tree.IfStatement,)):
        count += 1  # Conta o próprio if
        # else-if é um IfStatement dentro do else
        if node.else_statement:
            if isinstance(node.else_statement, javalang.tree.IfStatement):
                count += calculate_complexity(node.else_statement)
            else:
                count += _walk_statements(node.else_statement)
        count += _walk_statements(node.then_statement)
    return count

def _walk_statements(node) -> int:
    if node is None:
        return 0
    count = 0
    for child in (node if isinstance(node, list) else [node]):
        if isinstance(child, javalang.tree.IfStatement):
            count += 1 + calculate_complexity(child)
        elif hasattr(child, 'children'):
            for sub in child.children:
                if sub:
                    count += _walk_statements(sub)
    return count

def analyze_file(filepath: str) -> dict:
    source = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    try:
        tree = javalang.parse.parse(source)
    except javalang.parser.JavaSyntaxError:
        return {"error": "Syntax error", "methods": []}

    results = []
    for _, class_decl in tree.filter(javalang.tree.ClassDeclaration):
        for method in class_decl.methods:
            cc = 1  # Base = 1
            if method.body:
                for statement in method.body:
                    if isinstance(statement, javalang.tree.IfStatement):
                        cc += 1 + calculate_complexity(statement)
            
            results.append({
                "class": class_decl.name,
                "method": method.name,
                "complexity": cc,
                "score": classify_complexity(cc)
            })
    return {"methods": results}

def classify_complexity(cc: int) -> str:
    if cc <= 10:   return "LOW"
    if cc <= 20:   return "MODERATE"
    if cc <= 50:   return "HIGH"
    return "CRITICAL"