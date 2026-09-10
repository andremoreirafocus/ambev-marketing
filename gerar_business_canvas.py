#!/usr/bin/env python3
"""Gera NewBusinessCanvas.html a partir de BusinessCanvas.md, sem dependências.

Uso: python3 gerar_business_canvas.py
Outra versão: python3 gerar_business_canvas.py --entrada BusinessCanvas_MichelobUltra.md
Com --entrada, a saída padrão usa o mesmo nome e extensão .html; --saida permite outro nome.
Os caminhos são relativos à pasta deste script, independentemente do terminal.
Edite os textos e listas do Markdown, preservando os títulos dos nove blocos.
O HTML original não é necessário durante a geração.
"""
import argparse
from html import escape
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "BusinessCanvas.md"
OUTPUT = BASE / "NewBusinessCanvas.html"
BLOCKS = (
    ("Parceiros-chave", "partners"),
    ("Atividades-chave", "activities"),
    ("Recursos-chave", "resources"),
    ("Proposta de Valor", "value"),
    ("Relacionamento com clientes", "relations"),
    ("Canais", "channels"),
    ("Segmentação de clientes", "segments"),
    ("Estrutura de custo", "cost"),
    ("Fontes de Receita", "revenue"),
)

CSS = '\n* { box-sizing: border-box; }\nbody { margin: 0; background: #e8e8e8; color: #111; font-family: Arial, sans-serif; }\n.page { width: 1500px; margin: 24px auto; padding: 24px 46px 30px; background: #fff; }\nheader { min-height: 135px; }\nh1 { margin: 0 0 14px; font-size: 27px; font-weight: 500; }\nheader p { max-width: 1000px; margin: 0; font-size: 16px; line-height: 1.5; }\n.canvas {\n  display: grid;\n  grid-template-columns: repeat(10, minmax(0, 1fr));\n  grid-template-rows: minmax(250px, auto) minmax(250px, auto) minmax(210px, auto);\n  grid-template-areas:\n    "partners partners activities activities value value relations relations segments segments"\n    "partners partners resources resources value value channels channels segments segments"\n    "cost cost cost cost cost revenue revenue revenue revenue revenue";\n  gap: 14px 12px;\n}\nsection { min-width: 0; padding: 16px 18px 20px; background: #f2f2f2; }\nh2 { margin: 0 0 22px; text-align: center; font-size: 18px; line-height: 1.3; font-weight: 400; }\nul { margin: 0; padding-left: 17px; }\nli { margin-bottom: 13px; font-size: 14px; line-height: 1.45; overflow-wrap: break-word; }\nli:last-child { margin-bottom: 0; }\n.partners { grid-area: partners; }\n.activities { grid-area: activities; }\n.resources { grid-area: resources; }\n.value { grid-area: value; }\n.relations { grid-area: relations; }\n.channels { grid-area: channels; }\n.segments { grid-area: segments; }\n.cost { grid-area: cost; margin-top: 5px; margin-right: 9px; }\n.revenue { grid-area: revenue; margin-top: 5px; margin-left: 9px; }\nfooter { margin-top: 22px; font-size: 13px; line-height: 1.5; color: #444; }\nfooter p { margin: 7px 0; }\na { color: #135a78; }\n@media (max-width: 1548px) { .page { margin: 16px; } }\n@page { size: A3 landscape; margin: 10mm; }\n@media print {\n  body { background: #fff; }\n  .page { width: 100%; margin: 0; padding: 0; }\n  header { min-height: 85px; }\n  h1 { font-size: 23px; }\n  header p { font-size: 13px; }\n  .canvas { grid-template-rows: minmax(225px, auto) minmax(225px, auto) minmax(175px, auto); }\n  section { padding: 12px 14px; break-inside: avoid; }\n  h2 { font-size: 16px; margin-bottom: 16px; }\n  li { font-size: 12px; line-height: 1.4; margin-bottom: 10px; }\n  footer { font-size: 10px; margin-top: 12px; }\n  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }\n}\n'


def inline(text):
    """Escapa HTML e permite apenas ênfase simples do Markdown."""
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return re.sub(r"\[([^\]]+)\]\(([A-Za-z0-9_.-]+\.(?:md|html|png|svg))\)", r'<a href="\2">\1</a>', text)


def render_body(lines):
    """Converte parágrafos e listas; aceita itens quebrados em várias linhas."""
    parts, paragraph, items = [], [], []

    def flush_paragraph():
        if paragraph:
            parts.append("<p>" + inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()

    def flush_list():
        if items:
            parts.append("<ul>" + "".join("<li>" + inline(i) + "</li>" for i in items) + "</ul>")
            items.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
        elif stripped.startswith("- "):
            flush_paragraph()
            items.append(stripped[2:])
        elif items and line[:1].isspace():
            items[-1] += " " + stripped
        else:
            flush_list()
            paragraph.append(stripped)
    flush_paragraph()
    flush_list()
    return "".join(parts)


def generate(markdown, source_name="BusinessCanvas.md"):
    title, intro, sections = None, [], {}
    current = intro
    for line in markdown.splitlines():
        if line.startswith("# "):
            if title is not None:
                raise ValueError("Use apenas um título principal (#).")
            title = line[2:].strip()
        elif line.startswith("## "):
            heading = line[3:].strip()
            if heading in sections:
                raise ValueError("Seção repetida: " + heading)
            current = sections[heading] = []
        else:
            current.append(line)
    if not title:
        raise ValueError("O Markdown precisa de um título principal (#).")
    for heading, _ in BLOCKS:
        if heading not in sections or not any(line.strip() for line in sections[heading]):
            raise ValueError("Bloco obrigatório ausente ou vazio: " + heading)

    # Os links de navegação são recriados; textos editoriais vêm do Markdown.
    intro = [line for line in intro if not line.startswith(("Modelo de referência:", "Versão visual para apresentação ou impressão:"))]
    intro_parts = re.split(r"\n\s*\n", "\n".join(intro).strip(), maxsplit=1)
    subtitle = render_body(intro_parts[0].splitlines())
    context = render_body(intro_parts[1].splitlines()) if len(intro_parts) > 1 else ""
    blocks = "".join(
        '<section class="' + area + '"><h2>' + escape(heading) + '</h2>'
        + render_body(sections[heading]) + '</section>'
        for heading, area in BLOCKS
    )
    block_titles = {heading for heading, _ in BLOCKS}
    extra = "".join(
        '<p><strong>' + escape(heading) + '</strong></p>' + render_body(lines)
        for heading, lines in sections.items() if heading not in block_titles
    )
    return (
        '<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>' + escape(title) + '</title>\n<style>' + CSS + '</style></head>'
        '<body><main class="page"><header><h1><strong>BUSINESS CANVAS</strong> / BASE METODOLÓGICA</h1>'
        '<p>' + inline(title) + '</p>' + subtitle + '</header>'
        '<div class="canvas">' + blocks + '</div><footer>' + context + extra
        + '<p>Detalhamento e hipóteses: <a href="' + escape(source_name, quote=True) + '">' + escape(source_name) + '</a>'
        ' · Estrutura de referência: <a href="BusinessCanvas.png">BusinessCanvas.png</a></p>'
        '</footer></main></body></html>\n'
    )


def main():
    parser = argparse.ArgumentParser(description="Gera um Canvas HTML a partir de Markdown.")
    parser.add_argument("--entrada", type=Path, default=SOURCE)
    parser.add_argument("--saida", type=Path)
    args = parser.parse_args()
    source = (BASE / args.entrada).resolve()
    output = (BASE / args.saida).resolve() if args.saida else (OUTPUT if source == SOURCE else source.with_suffix(".html"))
    if output == source:
        parser.error("A saída deve ser diferente da entrada.")
    if output.parent != source.parent:
        parser.error("Mantenha o HTML na mesma pasta do Markdown para preservar os links relativos.")
    try:
        html = generate(source.read_text(encoding="utf-8"), source.name)
        output.write_text(html, encoding="utf-8")
    except (OSError, ValueError) as error:
        raise SystemExit("Erro ao gerar Canvas: " + str(error)) from error
    print("HTML gerado: " + str(output))


if __name__ == "__main__":
    main()
