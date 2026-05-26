import asyncio
import httpx
import time
import subprocess
import shutil
import re
from pathlib import Path


# ─────────────────────────────────────────
# 1. Detecção de build tool
# ─────────────────────────────────────────

def detect_build_tool(repo_path: str) -> str | None:
    path = Path(repo_path)
    if (path / "pom.xml").exists():
        return "maven"
    if (path / "build.gradle").exists():
        return "gradle"
    if (path / "build.gradle.kts").exists():
        return "gradle_kts"
    return None


# ─────────────────────────────────────────
# 2. Geração dinâmica do Dockerfile
# ─────────────────────────────────────────

def generate_dockerfile(repo_path: str, build_tool: str) -> str:
    if build_tool == "maven":
        content = """FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn package -DskipTests -q

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
"""
    else:  # gradle / gradle_kts
        content = """FROM gradle:8.5-jdk17 AS build
WORKDIR /app
COPY . .
RUN gradle build -x test --quiet

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
"""

    dockerfile_path = Path(repo_path) / "Dockerfile.audit"
    dockerfile_path.write_text(content, encoding="utf-8")
    return str(dockerfile_path)


# ─────────────────────────────────────────
# 3. Build e run do container
# ─────────────────────────────────────────

IMAGE_NAME = "audit-target"
CONTAINER_NAME = "audit-target-container"
APP_PORT = 8080
HOST_PORT = 9090  # porta no host para evitar conflito


def docker_build(repo_path: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["docker", "build", "-f", "Dockerfile.audit", "-t", IMAGE_NAME, "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )
        if result.returncode != 0:
            return False, result.stderr[-2000:]  # últimas 2000 chars do erro
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "Build timeout (5 minutos excedido)"
    except Exception as e:
        return False, str(e)


def docker_run() -> tuple[bool, str]:
    # Para container anterior se existir
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        capture_output=True
    )

    try:
        result = subprocess.run(
            [
                "docker", "run", "-d",
                "--name", CONTAINER_NAME,
                "-p", f"{HOST_PORT}:{APP_PORT}",
                IMAGE_NAME
            ],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return False, result.stderr
        return True, ""
    except Exception as e:
        return False, str(e)


def docker_stop():
    subprocess.run(
        ["docker", "rm", "-f", CONTAINER_NAME],
        capture_output=True
    )


# ─────────────────────────────────────────
# 4. Health check — aguarda aplicação subir
# ─────────────────────────────────────────

def wait_for_app(timeout: int = 60) -> bool:
    base_url = f"http://localhost:{HOST_PORT}"
    endpoints = ["/actuator/health", "/health", "/", "/api"]

    start = time.time()
    while time.time() - start < timeout:
        for endpoint in endpoints:
            try:
                resp = httpx.get(f"{base_url}{endpoint}", timeout=3)
                if resp.status_code < 500:
                    return True
            except Exception:
                pass
        time.sleep(2)

    return False


# ─────────────────────────────────────────
# 5. Parser de rotas Spring
# ─────────────────────────────────────────

ROUTE_ANNOTATIONS = [
    r'@GetMapping\s*\(\s*["\']([^"\']+)["\']',
    r'@PostMapping\s*\(\s*["\']([^"\']+)["\']',
    r'@PutMapping\s*\(\s*["\']([^"\']+)["\']',
    r'@DeleteMapping\s*\(\s*["\']([^"\']+)["\']',
    r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']',
    r'@GetMapping\s*\(\s*value\s*=\s*["\']([^"\']+)["\']',
    r'@PostMapping\s*\(\s*value\s*=\s*["\']([^"\']+)["\']',
]

CLASS_MAPPING = r'@RequestMapping\s*\(\s*["\']([^"\']+)["\']'

METHOD_TYPE = {
    "GetMapping": "GET",
    "PostMapping": "POST",
    "PutMapping": "PUT",
    "DeleteMapping": "DELETE",
    "RequestMapping": "GET",
}


def parse_routes(repo_path: str) -> list[dict]:
    routes = []
    java_files = list(Path(repo_path).rglob("*.java"))

    for filepath in java_files:
        source = filepath.read_text(encoding="utf-8", errors="ignore")

        # Pega prefixo da classe se tiver @RequestMapping na classe
        class_prefix = ""
        class_match = re.search(CLASS_MAPPING, source)
        if class_match:
            class_prefix = class_match.group(1).rstrip("/")

        for annotation_pattern in ROUTE_ANNOTATIONS:
            for match in re.finditer(annotation_pattern, source):
                path = match.group(1)
                if not path.startswith("/"):
                    path = "/" + path

                full_path = class_prefix + path

                # Detecta o tipo HTTP pelo nome da anotação
                annotation_name = re.search(r'@(\w+Mapping)', match.group(0))
                http_method = "GET"
                if annotation_name:
                    http_method = METHOD_TYPE.get(annotation_name.group(1), "GET")

                routes.append({
                    "route": full_path,
                    "method": http_method,
                    "file": filepath.name,
                })

    # Remove duplicatas
    seen = set()
    unique_routes = []
    for r in routes:
        key = f"{r['method']}:{r['route']}"
        if key not in seen:
            seen.add(key)
            unique_routes.append(r)

    return unique_routes[:10]  # Limita a 10 rotas para não demorar demais


# ─────────────────────────────────────────
# 6. Benchmarking real com httpx async
# ─────────────────────────────────────────

async def measure_latency_async(url: str, count: int) -> dict:
    latencies = []
    errors = 0
    batch_size = 50

    async with httpx.AsyncClient(timeout=5) as client:
        start = time.perf_counter()

        for i in range(0, count, batch_size):
            batch = [client.get(url) for _ in range(min(batch_size, count - i))]
            results = await asyncio.gather(*batch, return_exceptions=True)
            for r in results:
                if isinstance(r, Exception):
                    errors += 1
                else:
                    latencies.append(r.elapsed.total_seconds() * 1000)

        end = time.perf_counter()

    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0

    return {
        "count": count,
        "avg_latency_ms": avg_latency,
        "total_time_ms": round((end - start) * 1000, 2),
        "errors": errors,
        "success_rate": round((count - errors) / count * 100, 1)
    }


def benchmark_route(route: str) -> dict:
    base_url = f"http://localhost:{HOST_PORT}"
    url = base_url + route
    loads = [10, 50, 100, 500]
    results = {}

    for load in loads:
        result = asyncio.run(measure_latency_async(url, load))
        results[str(load)] = result

    # Calcula % de aumento de latência
    base_latency = results["10"]["avg_latency_ms"]
    for load in ["50", "100", "500"]:
        current = results[load]["avg_latency_ms"]
        if base_latency > 0:
            pct_increase = round(((current - base_latency) / base_latency) * 100, 1)
            results[load]["latency_increase_pct"] = pct_increase
        else:
            results[load]["latency_increase_pct"] = 0

    results["10"]["latency_increase_pct"] = 0
    return results


def classify_latency(avg_ms: float) -> str:
    if avg_ms <= 100:  return "LOW"
    if avg_ms <= 300:  return "MODERATE"
    if avg_ms <= 1000: return "HIGH"
    return "CRITICAL"


# ─────────────────────────────────────────
# 7. Orquestrador do módulo
# ─────────────────────────────────────────

def run(repo: dict) -> dict:
    repo_path = repo["repo_path"]

    # 1. Detecta build tool
    build_tool = detect_build_tool(repo_path)
    if not build_tool:
        return {
            "module": "Performance",
            "status": "skipped",
            "reason": "Nenhum build tool detectado (Maven ou Gradle)"
        }

    # 2. Gera Dockerfile
    generate_dockerfile(repo_path, build_tool)

    # 3. Build
    print("[Módulo 2] Compilando projeto via Docker...")
    build_ok, build_error = docker_build(repo_path)
    if not build_ok:
        return {
            "module": "Performance",
            "status": "build_failed",
            "reason": f"Falha na compilação: {build_error}"
        }

    # 4. Run
    print("[Módulo 2] Subindo container...")
    run_ok, run_error = docker_run()
    if not run_ok:
        docker_stop()
        return {
            "module": "Performance",
            "status": "run_failed",
            "reason": f"Falha ao subir container: {run_error}"
        }

    # 5. Aguarda subir
    print("[Módulo 2] Aguardando aplicação subir...")
    app_ready = wait_for_app(timeout=60)
    if not app_ready:
        docker_stop()
        return {
            "module": "Performance",
            "status": "timeout",
            "reason": "Aplicação não respondeu em 60 segundos — pode requerer banco de dados ou configuração externa"
        }

    # 6. Parseia rotas
    routes = parse_routes(repo_path)
    if not routes:
        docker_stop()
        return {
            "module": "Performance",
            "status": "no_routes",
            "reason": "Nenhuma rota Spring encontrada (@GetMapping, @PostMapping, etc)"
        }

    print(f"[Módulo 2] {len(routes)} rotas encontradas. Iniciando benchmark...")

    # 7. Benchmarking
    route_results = []
    for route_info in routes:
        # Só testa rotas GET para evitar erros de body inválido
        if route_info["method"] != "GET":
            continue

        print(f"[Módulo 2] Benchmarkando {route_info['route']}...")
        latency_data = benchmark_route(route_info["route"])
        base_latency = latency_data["100"]["avg_latency_ms"]

        route_results.append({
            "route": route_info["route"],
            "method": route_info["method"],
            "file": route_info["file"],
            "score": classify_latency(base_latency),
            "latency": latency_data
        })

    # 8. Para container
    docker_stop()

    # Rota mais lenta
    worst_route = max(route_results, key=lambda r: r["latency"]["100"]["avg_latency_ms"]) if route_results else None

    return {
        "module": "Performance",
        "status": "success",
        "build_tool": build_tool,
        "routes_found": len(routes),
        "routes_tested": len(route_results),
        "worst_route": worst_route,
        "routes": route_results
    }