from pathlib import Path
import javalang

def find_test_files(repo_path: str) -> list:
    return [
        str(f) for f in Path(repo_path).rglob("*.java")
        if any(p in f.name for p in ["Test", "Tests", "Spec"])
    ]

def find_production_files(repo_path: str) -> list:
    test_patterns = ["Test", "Tests", "Spec"]
    return [
        str(f) for f in Path(repo_path).rglob("*.java")
        if not any(p in f.name for p in test_patterns)
    ]

def count_executable_lines(filepath: str) -> int:
    """Conta linhas que não são comentário, blank, ou declaração."""
    count = 0
    for line in Path(filepath).read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped and \
           not stripped.startswith("//") and \
           not stripped.startswith("*") and \
           not stripped.startswith("/*") and \
           not stripped in ("{", "}", "};"):
            count += 1
    return count

def extract_referenced_classes(test_file: str) -> set:
    """Extrai quais classes de produção o teste referencia."""
    source = Path(test_file).read_text(encoding="utf-8", errors="ignore")
    referenced = set()
    try:
        tree = javalang.parse.parse(source)
        # Imports apontam para classes de produção
        for imp in tree.imports:
            class_name = imp.path.split(".")[-1]
            if not any(p in class_name for p in ["Test", "Mock", "Assert"]):
                referenced.add(class_name)
        # Tipos usados dentro dos métodos de teste
        for _, node in tree.filter(javalang.tree.ReferenceType):
            referenced.add(node.name)
    except:
        pass
    return referenced

def run(repo: dict) -> dict:
    repo_path = repo["repo_path"]

    test_files = find_test_files(repo_path)
    prod_files = find_production_files(repo_path)

    if not test_files:
        return {
            "module": "Reliability",
            "has_tests": False,
            "overall_coverage_pct": 0,
            "overall_score": "CRITICAL",
            "message": "Nenhum teste unitário encontrado"
        }

    # Coleta todas as classes referenciadas nos testes
    referenced_classes = set()
    for test_file in test_files:
        referenced_classes.update(extract_referenced_classes(test_file))

    # Analisa cada arquivo de produção
    file_results = []
    total_lines = 0
    total_covered = 0

    for filepath in prod_files:
        class_name = Path(filepath).stem
        lines = count_executable_lines(filepath)
        is_covered = class_name in referenced_classes

        covered_lines = lines if is_covered else 0
        total_lines += lines
        total_covered += covered_lines

        file_results.append({
            "file": Path(filepath).name,
            "class": class_name,
            "executable_lines": lines,
            "covered": is_covered,
            "coverage_pct": 100.0 if is_covered else 0.0,
            "score": "GOOD" if is_covered else "CRITICAL"
        })

    overall_pct = round((total_covered / total_lines) * 100, 2) if total_lines > 0 else 0

    return {
        "module": "Reliability",
        "has_tests": True,
        "test_files_found": len(test_files),
        "production_files": len(prod_files),
        "overall_coverage_pct": overall_pct,
        "overall_score": classify_coverage(overall_pct),
        "summary": {
            "total_lines": total_lines,
            "total_covered": total_covered,
            "classes_with_tests": len([f for f in file_results if f["covered"]]),
            "classes_without_tests": len([f for f in file_results if not f["covered"]]),
        },
        "files": file_results
    }

def classify_coverage(pct: float) -> str:
    if pct >= 80: return "GOOD"
    if pct >= 60: return "MODERATE"
    if pct >= 40: return "LOW"
    return "CRITICAL"