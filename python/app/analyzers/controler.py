from pathlib import Path
from app.analyzers import cyclomatic, cbo, dryness
from collections import Counter

def run(repo: dict) -> dict: 
    repo_path = repo["repo_path"]

    java_files = [str(f) for f in Path(repo_path).rglob("*.java")]

    cc_results = []
    cbo_results = []

    for filepath in java_files: 
        cc = cyclomatic.analyze_file(filepath)
        cc["file"] = filepath
        cc_results.append(cc)

        c = cbo.analyze_file(filepath)
        c['file'] = filepath
        cbo_results.append(c)

    dry_results = dryness.analyze_repository(java_files)

    all_methods = [m for f in cc_results for m in f.get("methods", [])]
    all_classes = [c for f in cbo_results for c in f.get("classes", [])]

    summary = {
        "total_files": len(java_files),
        "total_methods": len(all_methods),
        "cc_avg": round(sum(m["complexity"] for m in all_methods) / len(all_methods), 2) if all_methods else 0,
        "cc_worst": max(all_methods, key=lambda m: m["complexity"]) if all_methods else None,
        "cc_distribution": dict(Counter(m["score"] for m in all_methods)),
        "cbo_avg": round(sum(c["cbo"] for c in all_classes) / len(all_classes), 2) if all_classes else 0,
        "dryness_score": dry_results["score"],
        "duplicate_blocks": dry_results["total_duplicate_blocks"],
    }

    flagged_files = {
        "high_complexity": [
            f for f in cc_results
            if any(m["score"] in ("HIGH", "CRITICAL") for m in f.get("methods", []))
        ],
        "high_cbo": [
            f for f in cbo_results
            if any(c["score"] in ("HIGH", "CRITICAL") for c in f.get("classes", []))
        ],
    }

    return {
    "module": "Maintainability",
    "summary": summary,
    "flagged_files": flagged_files,
    "duplication": dry_results,
    "cbo": cbo_results,                        
    "cyclomatic_complexity": cc_results,    
    }