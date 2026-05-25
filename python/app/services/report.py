from datetime import datetime

def score_badge(score: str) -> str:
    colors = {
        "LOW":       ("#e6f4ea", "#2d6a4f", "LOW"),
        "MODERATE":  ("#fff8e1", "#7d5a00", "MODERATE"),
        "HIGH":      ("#fdecea", "#9b2335", "HIGH"),
        "CRITICAL":  ("#f7c1c1", "#791f1f", "CRITICAL"),
        "GOOD":      ("#e6f4ea", "#2d6a4f", "GOOD"),
        "EXCELLENT": ("#e6f4ea", "#2d6a4f", "EXCELLENT"),
    }
    bg, color, label = colors.get(score, ("#f1efeb", "#444", score))
    return f'<span style="background:{bg};color:{color};padding:3px 10px;border-radius:6px;font-size:12px;font-weight:500;">{label}</span>'

def build_report(data: dict) -> str:
    url      = data.get("url", "—")
    name     = data.get("name", "Repositório")
    r1       = data.get("result1", {})
    r3       = data.get("result3", {})
    date_str = datetime.now().strftime("%d/%m/%Y %H:%M")

    summary1   = r1.get("summary", {})
    flagged    = r1.get("flagged_files", {})
    dup        = r1.get("duplication", {})
    cbo_files  = r1.get("cbo", [])
    cc_files   = r1.get("cyclomatic_complexity", [])

    # Fallback: se não vieram os arrays completos, usa os flagged
    if not cbo_files:
        cbo_files = flagged.get("high_cbo", [])
    if not cc_files:
        cc_files = flagged.get("high_complexity", [])

    cc_avg     = summary1.get("cc_avg", 0)
    cc_worst   = summary1.get("cc_worst", {})
    cc_dist    = summary1.get("cc_distribution", {})
    cbo_avg    = summary1.get("cbo_avg", 0)
    total_files= summary1.get("total_files", 0)
    total_meth = summary1.get("total_methods", 0)

    dup_ratio  = dup.get("duplication_ratio", 0)
    dup_blocks = dup.get("total_duplicate_blocks", 0)
    dup_score  = dup.get("score", "—")

    cov_pct    = r3.get("overall_coverage_pct", 0)
    cov_score  = r3.get("overall_score", "—")
    has_tests  = r3.get("has_tests", False)
    test_files = r3.get("test_files_found", 0)
    prod_files = r3.get("production_files", 0)
    r3_summary = r3.get("summary", {})
    with_tests = r3_summary.get("classes_with_tests", 0)
    without_tests = r3_summary.get("classes_without_tests", 0)
    r3_files   = r3.get("files", [])

    # ISO conclusion
    def iso_status(ok: bool) -> str:
        if ok:
            return '<span style="color:#2d6a4f;font-weight:500;">✓ Conforme</span>'
        return '<span style="color:#9b2335;font-weight:500;">✗ Não conforme</span>'

    cc_ok  = cc_avg <= 10
    cbo_ok = float(cbo_avg) <= 10
    dup_ok = dup_score in ("EXCELLENT", "LOW")
    cov_ok = float(cov_pct) >= 60

    # CC distribution bars
    total_methods_dist = sum(cc_dist.values()) or 1
    def dist_bar(label, count, color):
        pct = round(count / total_methods_dist * 100, 1)
        return f"""
        <tr>
          <td style="font-size:13px;color:#666;width:80px;padding:4px 0;">{label}</td>
          <td style="padding:4px 8px;">
            <div style="background:#f1efeb;border-radius:4px;height:8px;width:100%;">
              <div style="background:{color};height:8px;border-radius:4px;width:{pct}%;"></div>
            </div>
          </td>
          <td style="font-size:13px;color:#444;width:40px;text-align:right;padding:4px 0;">{count}</td>
        </tr>"""

    # CC file rows
    cc_rows = ""
    for f in cc_files:
        filepath = f.get("file", "")
        filename = filepath.replace("\\", "/").split("/")[-1]
        methods  = f.get("methods", [])
        for m in methods:
            cc_rows += f"""
            <tr>
              <td style="padding:6px 8px;font-size:12px;color:#444;font-family:monospace;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{filename}">{filename}</td>
              <td style="padding:6px 8px;font-size:12px;color:#444;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{m.get('class','')}">{m.get('class','')}</td>
              <td style="padding:6px 8px;font-size:12px;color:#444;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{m.get('method','')}">{m.get('method','')}</td>
              <td style="padding:6px 8px;font-size:12px;text-align:center;width:50px;">{m.get('complexity','')}</td>
              <td style="padding:6px 8px;font-size:12px;width:90px;">{score_badge(m.get('score',''))}</td>
            </tr>"""

    # CBO file rows
    cbo_rows = ""
    for f in cbo_files:
        filepath = f.get("file", "")
        filename = filepath.replace("\\", "/").split("/")[-1]
        classes  = f.get("classes", [])
        for c in classes:
            cbo_rows += f"""
            <tr>
              <td style="padding:6px 8px;font-size:12px;color:#444;font-family:monospace;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{filename}">{filename}</td>
              <td style="padding:6px 8px;font-size:12px;color:#444;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="{c.get('class','')}">{c.get('class','')}</td>
              <td style="padding:6px 8px;font-size:12px;text-align:center;width:50px;">{c.get('cbo','')}</td>
              <td style="padding:6px 8px;font-size:12px;width:90px;">{score_badge(c.get('score',''))}</td>
            </tr>"""

    # Coverage file rows
    cov_rows = ""
    for f in r3_files:
        cov_rows += f"""
        <tr>
          <td style="padding:6px 8px;font-size:12px;color:#444;font-family:monospace;">{f.get('file','')}</td>
          <td style="padding:6px 8px;font-size:12px;text-align:center;">{'Sim' if f.get('covered') else 'Não'}</td>
          <td style="padding:6px 8px;font-size:12px;text-align:center;">{f.get('coverage_pct',0)}%</td>
          <td style="padding:6px 8px;font-size:12px;">{score_badge(f.get('score',''))}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Relatório ISO/IEC 25010 — {name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f7f6f3; color: #1a1a1a; }}
  .page {{ max-width: 960px; margin: 0 auto; padding: 2rem 1.5rem; }}

  /* Header */
  .header {{ background: #fff; border: 0.5px solid #e0ddd6; border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; }}
  .header h1 {{ font-size: 20px; font-weight: 500; margin-bottom: 8px; }}
  .header-meta {{ display: flex; gap: 2rem; font-size: 13px; color: #666; }}
  .header-meta span {{ display: flex; align-items: center; gap: 6px; }}

  /* Section */
  .section {{ background: #fff; border: 0.5px solid #e0ddd6; border-radius: 12px; padding: 1.5rem 2rem; margin-bottom: 1.5rem; }}
  .section-title {{ font-size: 16px; font-weight: 500; margin-bottom: 1.25rem; padding-bottom: 10px; border-bottom: 0.5px solid #e0ddd6; display: flex; align-items: center; gap: 8px; }}
  .section-subtitle {{ font-size: 14px; font-weight: 500; color: #444; margin: 1.25rem 0 0.75rem; }}

  /* Summary cards */
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 1.25rem; }}
  .card {{ background: #f7f6f3; border-radius: 8px; padding: 12px 14px; }}
  .card-label {{ font-size: 11px; color: #888; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.04em; }}
  .card-value {{ font-size: 22px; font-weight: 500; }}
  .card-sub {{ font-size: 11px; color: #888; margin-top: 2px; }}

  /* Highlight row */
  .highlight {{ background: #f7f6f3; border-radius: 8px; padding: 10px 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; font-size: 13px; }}
  .highlight-label {{ color: #666; }}
  .highlight-value {{ font-weight: 500; font-family: monospace; }}

  /* Table */
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  thead tr {{ background: #f7f6f3; }}
  th {{ padding: 8px; text-align: left; font-weight: 500; font-size: 12px; color: #666; border-bottom: 0.5px solid #e0ddd6; }}
  tbody tr:nth-child(even) {{ background: #fafaf8; }}
  tbody tr:hover {{ background: #f1efeb; }}
  td {{ border-bottom: 0.5px solid #f1efeb; }}

  /* Accordion */
  details {{ margin-top: 1rem; border: 0.5px solid #e0ddd6; border-radius: 8px; overflow: hidden; }}
  summary {{ padding: 10px 14px; font-size: 13px; font-weight: 500; color: #444; cursor: pointer; background: #f7f6f3; list-style: none; display: flex; align-items: center; gap: 6px; }}
  summary::-webkit-details-marker {{ display: none; }}
  summary::before {{ content: '▶'; font-size: 10px; transition: transform 0.2s; }}
  details[open] summary::before {{ transform: rotate(90deg); }}
  .accordion-body {{ padding: 0; overflow-x: auto; }}

  /* Module 2 placeholder */
  .placeholder {{ background: #f7f6f3; border: 0.5px dashed #ccc; border-radius: 8px; padding: 2rem; text-align: center; color: #999; font-size: 14px; }}

  /* ISO table */
  .iso-ok   {{ color: #2d6a4f; font-weight: 500; }}
  .iso-fail {{ color: #9b2335; font-weight: 500; }}

  /* Coverage bar */
  .cov-bar-wrap {{ background: #f1efeb; border-radius: 6px; height: 10px; margin: 8px 0; overflow: hidden; }}
  .cov-bar {{ height: 100%; border-radius: 6px; background: #f0b429; }}
</style>
</head>
<body>
<div class="page">

  <!-- Header -->
  <div class="header">
    <h1>Relatório de Qualidade — {name}</h1>
    <div class="header-meta">
      <span>{url}</span>
      <span>{date_str}</span>
    </div>
  </div>

  <!-- Módulo 1 -->
  <div class="section">
    <div class="section-title">Módulo 1 — Manutenibilidade</div>

    <div class="cards">
      <div class="card">
        <div class="card-label">arquivos</div>
        <div class="card-value">{total_files}</div>
      </div>
      <div class="card">
        <div class="card-label">métodos</div>
        <div class="card-value">{total_meth}</div>
      </div>
      <div class="card">
        <div class="card-label">cc médio</div>
        <div class="card-value">{cc_avg}</div>
        <div class="card-sub">complexidade ciclomática</div>
      </div>
      <div class="card">
        <div class="card-label">cbo médio</div>
        <div class="card-value">{cbo_avg}</div>
        <div class="card-sub">acoplamento</div>
      </div>
      <div class="card">
        <div class="card-label">duplicação</div>
        <div class="card-value">{dup_ratio}%</div>
        <div class="card-sub">{dup_blocks} blocos</div>
      </div>
    </div>

    <!-- CC -->
    <div class="section-subtitle">Complexidade Ciclomática</div>
    <div class="highlight">
      <span class="highlight-label">método mais complexo</span>
      <span class="highlight-value">{cc_worst.get('class','')}.{cc_worst.get('method','')} — CC {cc_worst.get('complexity','')}</span>
      {score_badge(cc_worst.get('score',''))}
    </div>
    <table style="margin-top:8px;">
      <tbody>
        {dist_bar('LOW',      cc_dist.get('LOW',0),      '#52b788')}
        {dist_bar('MODERATE', cc_dist.get('MODERATE',0), '#f0b429')}
        {dist_bar('HIGH',     cc_dist.get('HIGH',0),     '#e07a5f')}
        {dist_bar('CRITICAL', cc_dist.get('CRITICAL',0), '#c1121f')}
      </tbody>
    </table>

    <details>
      <summary>detalhes por arquivo — complexidade ciclomática</summary>
      <div class="accordion-body">
        <table style="table-layout:fixed;width:100%;">
          <thead><tr>
            <th style="width:200px;">Arquivo</th>
            <th style="width:150px;">Classe</th>
            <th style="width:150px;">Método</th>
            <th style="width:50px;text-align:center;">CC</th>
            <th style="width:90px;">Score</th>
          </tr></thead>
          <tbody>{cc_rows}</tbody>
        </table>
      </div>
    </details>

    <!-- CBO -->
    <div class="section-subtitle">Acoplamento entre Objetos (CBO)</div>
    <div class="highlight">
      <span class="highlight-label">média geral</span>
      <span class="highlight-value">{cbo_avg}</span>
    </div>
    <div class="highlight">
      <span class="highlight-label">classes com alto acoplamento</span>
      <span class="highlight-value">{len(flagged.get('high_cbo', []))} classes HIGH ou CRITICAL</span>
    </div>

    <details>
      <summary>detalhes por arquivo — acoplamento (CBO)</summary>
      <div class="accordion-body">
        <table style="table-layout:fixed;width:100%;">
          <thead><tr>
            <th style="width:200px;">Arquivo</th>
            <th style="width:200px;">Classe</th>
            <th style="width:50px;text-align:center;">CBO</th>
            <th style="width:90px;">Score</th>
          </tr></thead>
          <tbody>{cbo_rows}</tbody>
        </table>
      </div>
    </details>

    <!-- Duplicação -->
    <div class="section-subtitle">Duplicação de Código</div>
    <div class="highlight">
      <span class="highlight-label">taxa de duplicação</span>
      <span class="highlight-value">{dup_ratio}%</span>
      {score_badge(dup_score)}
    </div>
    <div class="highlight">
      <span class="highlight-label">blocos duplicados</span>
      <span class="highlight-value">{dup_blocks}</span>
    </div>
  </div>

  <!-- Módulo 2 -->
  <div class="section">
    <div class="section-title">Módulo 2 — Eficiência de Desempenho</div>
    <div class="placeholder">
      Análise dinâmica não disponível nesta versão.<br/>
      O benchmarking automático será implementado em versão futura.
    </div>
  </div>

  <!-- Módulo 3 -->
  <div class="section">
    <div class="section-title">Módulo 3 — Confiabilidade</div>

    <div class="cards">
      <div class="card">
        <div class="card-label">cobertura estimada</div>
        <div class="card-value">{cov_pct}%</div>
      </div>
      <div class="card">
        <div class="card-label">arquivos de teste</div>
        <div class="card-value">{test_files}</div>
      </div>
      <div class="card">
        <div class="card-label">classes cobertas</div>
        <div class="card-value">{with_tests}</div>
      </div>
      <div class="card">
        <div class="card-label">sem cobertura</div>
        <div class="card-value">{without_tests}</div>
      </div>
    </div>

    <div class="cov-bar-wrap">
      <div class="cov-bar" style="width:{cov_pct}%;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:12px;color:#888;margin-bottom:1rem;">
      <span>0%</span>
      <span>{score_badge(cov_score)}</span>
      <span>100%</span>
    </div>

    <details>
      <summary>detalhes por arquivo — cobertura de testes</summary>
      <div class="accordion-body">
        <table>
          <thead><tr><th>Arquivo</th><th style="text-align:center;">Coberto</th><th style="text-align:center;">Cobertura</th><th>Score</th></tr></thead>
          <tbody>{cov_rows}</tbody>
        </table>
      </div>
    </details>
  </div>

  <!-- ISO 25010 Conclusão -->
  <div class="section">
    <div class="section-title">Conclusão — ISO/IEC 25010</div>
    <table>
      <thead>
        <tr>
          <th>Característica</th>
          <th>Módulo</th>
          <th>Métrica</th>
          <th>Valor</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:8px;">Manutenibilidade</td>
          <td style="padding:8px;">Módulo 1</td>
          <td style="padding:8px;">Complexidade Ciclomática média</td>
          <td style="padding:8px;font-family:monospace;">{cc_avg}</td>
          <td style="padding:8px;">{iso_status(cc_ok)}</td>
        </tr>
        <tr>
          <td style="padding:8px;">Manutenibilidade</td>
          <td style="padding:8px;">Módulo 1</td>
          <td style="padding:8px;">Acoplamento médio (CBO)</td>
          <td style="padding:8px;font-family:monospace;">{cbo_avg}</td>
          <td style="padding:8px;">{iso_status(cbo_ok)}</td>
        </tr>
        <tr>
          <td style="padding:8px;">Manutenibilidade</td>
          <td style="padding:8px;">Módulo 1</td>
          <td style="padding:8px;">Taxa de duplicação</td>
          <td style="padding:8px;font-family:monospace;">{dup_ratio}%</td>
          <td style="padding:8px;">{iso_status(dup_ok)}</td>
        </tr>
        <tr>
          <td style="padding:8px;">Eficiência de Desempenho</td>
          <td style="padding:8px;">Módulo 2</td>
          <td style="padding:8px;">Benchmarking dinâmico</td>
          <td style="padding:8px;font-family:monospace;">—</td>
          <td style="padding:8px;color:#999;">Pendente</td>
        </tr>
        <tr>
          <td style="padding:8px;">Confiabilidade</td>
          <td style="padding:8px;">Módulo 3</td>
          <td style="padding:8px;">Cobertura de testes</td>
          <td style="padding:8px;font-family:monospace;">{cov_pct}%</td>
          <td style="padding:8px;">{iso_status(cov_ok)}</td>
        </tr>
      </tbody>
    </table>
  </div>

</div>
</body>
</html>"""

    return html