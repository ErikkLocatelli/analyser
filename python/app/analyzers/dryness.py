from pathlib import Path
from collections import defaultdict

MIN_BLOCK_SIZE = 5

def _get_normalized_lines(filepath: str) -> list[str]:
    """Remove linhas vazias e comentários para comparação."""
    lines = []
    for line in Path(filepath).read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("//") and not stripped.startswith("*"):
            lines.append(stripped)
    return lines

def analyze_repository(java_files: list[str]) -> dict:
    block_map = defaultdict(list)
    total_possible_blocks = 0

    for filepath in java_files:
        lines = _get_normalized_lines(filepath)
        file_blocks = len(lines) - MIN_BLOCK_SIZE + 1
        if file_blocks > 0:
            total_possible_blocks += file_blocks
            for i in range(file_blocks):
                block = tuple(lines[i:i + MIN_BLOCK_SIZE])
                block_map[block].append({"file": filepath, "line": i + 1})

    duplicates = []
    total_score = 0
    for block, occurrences in block_map.items():
        if len(occurrences) > 1:
            total_score += len(occurrences) - 1
            duplicates.append({
                "block_preview": list(block[:3]),
                "occurrences": occurrences,
                "count": len(occurrences)
            })

    # Normaliza pelo tamanho do projeto
    duplication_ratio = round((len(duplicates) / total_possible_blocks) * 100, 2) if total_possible_blocks > 0 else 0

    return {
        "total_duplicate_blocks": len(duplicates),
        "total_possible_blocks": total_possible_blocks,
        "duplication_ratio": duplication_ratio,  # % normalizado
        "total_score": total_score,
        "duplicates": duplicates,
        "score": classify_duplication(duplication_ratio)
    }

def classify_duplication(ratio: float) -> str:
    if ratio == 0:    return "EXCELLENT"
    if ratio <= 5:    return "LOW"
    if ratio <= 15:   return "MODERATE"
    return "HIGH"