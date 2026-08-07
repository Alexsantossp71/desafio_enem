#!/usr/bin/env python3
"""Valida o banco de questões do ENEM (public/).

Erros (bloqueiam, exit 1):
- JSON inválido ou conteúdo inesperado
- Ano da questão inconsistente com a pasta
- Disciplina fora do conjunto conhecido
- Gabarito (correctAlternative) fora das alternativas
- Letras de alternativas duplicadas ou fora de A–E
- isCorrect inconsistente com o gabarito

Avisos (não bloqueiam):
- Questões sem details.json (lacunas de extração)
- Imagens remotas (URLs) — validadas apenas a forma da URL
- Imagens locais inexistentes

Uso:  python3 scripts/validate_questions.py
"""
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent / "public"

DISCIPLINES = {
    "ciencias-humanas",
    "ciencias-natureza",
    "linguagens",
    "matematica",
}

errors: list[str] = []
warnings: list[str] = []
total = 0
total_dirs = 0


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


# 1. exams.json
exams_path = ROOT / "exams.json"
exam_years: set = set()
try:
    exams = json.loads(exams_path.read_text(encoding="utf-8"))
    exam_years = {
        e.get("year") for e in exams
    } if isinstance(exams, list) else set(exams.keys())
    exam_years = {int(y) for y in exam_years if str(y).isdigit()}
except Exception as exc:  # noqa: BLE001
    err(f"exams.json inválido: {exc}")

# 2. Anos
year_dirs = sorted(
    p for p in ROOT.iterdir()
    if p.is_dir() and p.name.isdigit()
)
if not year_dirs:
    err("Nenhum ano encontrado em public/")
print(f"✔ {len(year_dirs)} anos: {year_dirs[0].name}–{year_dirs[-1].name}" if year_dirs else "✘ nenhum ano")

for year_dir in year_dirs:
    year = int(year_dir.name)
    if exam_years and year not in exam_years:
        warn(f"{year}: não listado em exams.json")

    meta = year_dir / "details.json"
    if not meta.exists():
        warn(f"{year}: falta details.json")
    else:
        try:
            meta_data = json.loads(meta.read_text(encoding="utf-8"))
            if not isinstance(meta_data, dict) or not meta_data:
                err(f"{year}/details.json: metadados vazios ou inválidos")
        except Exception as exc:  # noqa: BLE001
            err(f"{year}/details.json: JSON inválido ({exc})")

    qdir = year_dir / "questions"
    if not qdir.exists():
        err(f"{year}: pasta questions/ ausente")
        continue

    # 3. Questões
    q_dirs = sorted(p for p in qdir.iterdir() if p.is_dir())
    total_dirs += len(q_dirs)
    for qd in q_dirs:
        qfile = qd / "details.json"
        if not qfile.exists():
            # Diretório com imagens mas sem metadados — lacuna conhecida
            n_files = len([f for f in qd.iterdir() if f.is_file()])
            warn(f"{year}/{qd.name}: sem details.json ({n_files} arquivo(s) na pasta)")
            continue

        total += 1
        try:
            q = json.loads(qfile.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            err(f"{year}/{qd.name}/details.json: JSON inválido ({exc})")
            continue

        if not isinstance(q, dict):
            err(f"{year}/{qd.name}: conteúdo não é objeto JSON")
            continue

        if not q.get("title"):
            err(f"{year}/{qd.name}: sem título")
        if not isinstance(q.get("index"), int):
            err(f"{year}/{qd.name}: índice ausente ou não inteiro")
        if q.get("year") != year:
            err(f"{year}/{qd.name}: year ({q.get('year')}) difere da pasta ({year})")
        if q.get("discipline") not in DISCIPLINES:
            err(f"{year}/{qd.name}: disciplina desconhecida ({q.get('discipline')!r})")

        alt_list = q.get("alternatives")
        if not isinstance(alt_list, list) or not alt_list:
            err(f"{year}/{qd.name}: sem alternativas")
            continue

        letters = [a.get("letter") for a in alt_list if isinstance(a, dict)]
        if len(letters) != len(set(letters)):
            err(f"{year}/{qd.name}: letras de alternativas duplicadas")
        if not all(l in "ABCDE" for l in letters):
            err(f"{year}/{qd.name}: letra de alternativa fora de A–E ({letters})")

        correct = q.get("correctAlternative")
        if correct not in letters:
            err(f"{year}/{qd.name}: gabarito ({correct!r}) não bate com alternativas {letters}")
            continue

        flagged = [a.get("letter") for a in alt_list
                   if isinstance(a, dict) and a.get("isCorrect")]
        if flagged and flagged != [correct]:
            err(f"{year}/{qd.name}: isCorrect {flagged} não bate com gabarito {correct}")

        # Imagens
        for alt in alt_list:
            fname = alt.get("file") if isinstance(alt, dict) else None
            if not fname:
                continue
            if str(fname).startswith(("http://", "https://")):
                if not is_valid_url(str(fname)):
                    err(f"{year}/{qd.name}: URL remota inválida: {fname}")
            elif not (qd / fname).exists():
                err(f"{year}/{qd.name}: imagem local não existe: {fname}")

        for fname in q.get("files") or []:
            if str(fname).startswith(("http://", "https://")):
                if not is_valid_url(str(fname)):
                    err(f"{year}/{qd.name}: URL remota inválida: {fname}")
            elif not (qd / fname).exists():
                err(f"{year}/{qd.name}: imagem local não existe: {fname}")

print(f"✔ {total} questões validadas ({total_dirs} diretórios no total)")

if warnings:
    print(f"\n⚠ {len(warnings)} aviso(s) (não bloqueiam) — mostrando até 5:")
    for w in warnings[:5]:
        print(f"  - {w}")
    if len(warnings) > 5:
        print(f"  ... e mais {len(warnings) - 5}")

if errors:
    print(f"\n✘ {len(errors)} erro(s) (mostrando até 20):")
    for e in errors[:20]:
        print(f"  - {e}")
    if len(errors) > 20:
        print(f"  ... e mais {len(errors) - 20}")
    sys.exit(1)

print("\n✔ Banco de questões OK!")
