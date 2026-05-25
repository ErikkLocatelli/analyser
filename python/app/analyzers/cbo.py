import javalang
from pathlib import Path

def analyze_file(filepath: str) -> dict:
    source = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    try:
        tree = javalang.parse.parse(source)
    except javalang.parser.JavaSyntaxError:
        return {"error": "Syntax error", "classes": []}

    results = []
    for _, class_decl in tree.filter(javalang.tree.ClassDeclaration):
        coupled_classes = set()

        # 1. Imports diretos
        for imp in tree.imports:
            # Ignora java.* e javax.* (stdlib)
            if not imp.path.startswith(("java.", "javax.")):
                coupled_classes.add(imp.path.split(".")[-1])

        # 2. Tipos dos campos (atributos)
        for field in class_decl.fields:
            _extract_type(field.type, coupled_classes)

        # 3. Tipos nos métodos (parâmetros e retorno)
        for method in class_decl.methods:
            if method.return_type:
                _extract_type(method.return_type, coupled_classes)
            for param in method.parameters:
                _extract_type(param.type, coupled_classes)

        # Remove a própria classe
        coupled_classes.discard(class_decl.name)

        results.append({
            "class": class_decl.name,
            "cbo": len(coupled_classes),
            "coupled_with": sorted(coupled_classes),
            "score": classify_cbo(len(coupled_classes))
        })

    return {"classes": results}

def _extract_type(type_node, result_set: set):
    if type_node is None:
        return
    if hasattr(type_node, 'name'):
        result_set.add(type_node.name)
    # Genéricos: List<Foo> → pega Foo também
    if hasattr(type_node, 'arguments') and type_node.arguments:
        for arg in type_node.arguments:
            if hasattr(arg, 'type'):
                _extract_type(arg.type, result_set)

def classify_cbo(cbo: int) -> str:
    if cbo <= 5:   return "LOW"
    if cbo <= 10:  return "MODERATE"
    if cbo <= 20:  return "HIGH"
    return "CRITICAL"