#!/usr/bin/env python3
"""Met en page plan-de-communication.md en PDF (A4) avec la charte du spot Splash Party :
beige doré #C39E6E, textes blancs sur les aplats, logo WBR blanc, Anton (titres) + Helvetica
(Liberation Sans, métriques identiques à Helvetica, pour le texte courant).
Usage : python3 plan_pdf.py -> plan-de-communication.pdf
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageEnhance
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, ListFlowable, ListItem, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle, Frame, BaseDocTemplate)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "well-brunch-reel"))
import render as R  # noqa: E402  (logo WBR)

SAND = colors.HexColor("#C39E6E")
SAND_LIGHT = colors.HexColor("#F6EFE6")
INK = colors.HexColor("#1F1B16")
GREY = colors.HexColor("#6B6258")
WHITE = colors.white
FONTS = HERE.parent / "well-brunch-reel" / "fonts"
LIB = Path("/usr/share/fonts/truetype/liberation")
pdfmetrics.registerFont(TTFont("Anton", str(FONTS / "Anton-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Helv", str(LIB / "LiberationSans-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Helv-Bold", str(LIB / "LiberationSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Helv-Italic", str(LIB / "LiberationSans-Italic.ttf")))
pdfmetrics.registerFontFamily("Helv", normal="Helv", bold="Helv-Bold", italic="Helv-Italic", boldItalic="Helv-Bold")

PW, PH = A4
M = 18 * mm
TMP = HERE / ".pdf-tmp"
TMP.mkdir(exist_ok=True)

# ---------------------------------------------------------------- éléments graphiques
logo = R.LOGO.copy()
logo.paste(Image.new("RGBA", logo.size, (255, 255, 255, 255)), (0, 0), logo.getchannel("A"))
logo.save(TMP / "logo-blanc.png")
photo = Image.open(HERE / "spot" / "sources" / "photo-enfants-mousse.jpg").convert("RGB")
pw_, ph_ = photo.size
target = PW / PH
crop_h = int(pw_ / target)
photo = photo.crop((0, (ph_ - crop_h) // 2, pw_, (ph_ - crop_h) // 2 + crop_h))
photo = ImageEnhance.Brightness(photo).enhance(0.62)
photo.save(TMP / "couverture.jpg", quality=90)

# ---------------------------------------------------------------- styles
ST = {
    "body": ParagraphStyle("body", fontName="Helv", fontSize=9.6, leading=13.6, textColor=INK, alignment=TA_LEFT,
                           spaceAfter=5),
    "h2": ParagraphStyle("h2", fontName="Anton", fontSize=20, leading=24, textColor=WHITE),
    "h3": ParagraphStyle("h3", fontName="Anton", fontSize=13.5, leading=17, textColor=SAND, spaceBefore=8,
                         spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="Helv", fontSize=8.4, leading=11, textColor=INK),
    "cellh": ParagraphStyle("cellh", fontName="Helv-Bold", fontSize=8.6, leading=11, textColor=WHITE),
    "bullet": ParagraphStyle("bullet", fontName="Helv", fontSize=9.6, leading=13.4, textColor=INK),
}

EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️‍\U0001F3FB-\U0001F3FF⏰-⏺]")


def inline(t):
    t = EMOJI.sub("", t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<font name='Helv-Italic' color='#8A6A3F'>\1</font>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
    return re.sub(r"\s{2,}", " ", t).strip()


class Band(Table):
    """Bandeau de titre de section : aplat beige, texte blanc (comme dans le spot)."""

    def __init__(self, text):
        super().__init__([[Paragraph(inline(text).upper(), ST["h2"])]], colWidths=[PW - 2 * M])
        self.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SAND),
                                  ("LEFTPADDING", (0, 0), (-1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 7),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                                  ("LINEBEFORE", (0, 0), (0, -1), 5, WHITE)]))


def md_table(lines):
    rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in lines]
    rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    ncol = len(rows[0])
    data = [[Paragraph(inline(c), ST["cellh"] if i == 0 else ST["cell"]) for c in r] for i, r in enumerate(rows)]
    avail = PW - 2 * M
    lens = [max(len(EMOJI.sub("", r[j])) for r in rows) for j in range(ncol)]
    lens = [min(max(l, 6), 70) for l in lens]
    widths = [avail * l / sum(lens) for l in lens]
    small = [j for j in range(ncol) if widths[j] < 17 * mm]      # colonnes courtes (N°, durée…) : largeur minimale
    if small:
        rest = avail - 17 * mm * len(small)
        big = sum(widths[j] for j in range(ncol) if j not in small)
        widths = [17 * mm if j in small else widths[j] * rest / big for j in range(ncol)]
    tb = Table(data, colWidths=widths, repeatRows=1)
    style = [("BACKGROUND", (0, 0), (-1, 0), SAND), ("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
             ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E3D5C1"))]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), SAND_LIGHT))
    tb.setStyle(TableStyle(style))
    return tb


def parse(md):
    story, i = [], 0
    lines = md.splitlines()
    para = []
    title = meta = None

    def flush():
        if para:
            story.append(Paragraph(inline(" ".join(para)), ST["body"]))
            para.clear()

    first_section = True
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s.startswith("# "):
            title = s[2:]
        elif s.startswith("## "):
            flush()
            if not first_section and s[3:4] in "6789" or s.startswith("## 1"):
                pass
            story.append(Spacer(1, 6 if first_section else 10))
            story.append(Band(s[3:]))
            story.append(Spacer(1, 7))
            first_section = False
        elif s.startswith("### "):
            flush()
            story.append(Paragraph(inline(s[4:]).upper(), ST["h3"]))
        elif s.startswith("|"):
            flush()
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i])
                i += 1
            story.append(md_table(block))
            story.append(Spacer(1, 7))
            continue
        elif re.match(r"^(\s*)([-*]|\d+\.)\s", ln):
            flush()
            items, numbered = [], bool(re.match(r"^\s*\d+\.", ln))
            while i < len(lines) and re.match(r"^(\s*)([-*]|\d+\.)\s", lines[i]):
                txt = re.sub(r"^\s*([-*]|\d+\.)\s", "", lines[i])
                indent = len(lines[i]) - len(lines[i].lstrip())
                items.append((indent, txt))
                i += 1
            flow = [ListItem(Paragraph(inline(t), ST["bullet"]), leftIndent=14 + ind * 4,
                             value=None) for ind, t in items]
            story.append(ListFlowable(flow, bulletType="1" if numbered else "bullet", start="1" if numbered else None,
                                      bulletColor=SAND, bulletFontName="Helv-Bold", bulletFontSize=9,
                                      leftIndent=14))
            story.append(Spacer(1, 5))
            continue
        elif s == "---" or not s:
            flush()
        else:
            if meta is None and title and not story:
                meta = (meta or "") + s
            else:
                para.append(s)
        i += 1
    flush()
    return title, story


# ---------------------------------------------------------------- pages
def cover(c, doc):
    c.saveState()
    c.drawImage(str(TMP / "couverture.jpg"), 0, 0, PW, PH)
    c.setFillColor(SAND)
    c.rect(0, 0, PW, 92 * mm, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.rect(0, 92 * mm, PW, 1.6 * mm, stroke=0, fill=1)
    lw = 46 * mm
    lh = lw * logo.height / logo.width
    c.drawImage(str(TMP / "logo-blanc.png"), (PW - lw) / 2, PH - 22 * mm - lh, lw, lh, mask="auto")
    c.setFont("Anton", 64)
    c.drawCentredString(PW / 2, 150 * mm, "SPLASH")
    c.drawCentredString(PW / 2, 125 * mm, "PARTY")
    c.setFont("Anton", 30)
    c.drawCentredString(PW / 2, 64 * mm, "PLAN DE COMMUNICATION")
    c.setFont("Helv-Bold", 12.5)
    c.drawCentredString(PW / 2, 50 * mm, "SAMEDI 5 DÉCEMBRE 2026  ·  8H – 18H")
    c.setFont("Helv", 11)
    c.drawCentredString(PW / 2, 41 * mm, "Wellbeing Resort  ·  Cocody Riviera 3, route M'Badon")
    c.drawCentredString(PW / 2, 33 * mm, "Campagne du 25 novembre au 6 décembre 2026")
    c.setFont("Helv", 9)
    c.drawCentredString(PW / 2, 17 * mm, "Préparé par ADOFE Communication")
    c.restoreState()


def page(c, doc):
    c.saveState()
    c.setFillColor(SAND)
    c.rect(0, PH - 13 * mm, PW, 13 * mm, stroke=0, fill=1)
    lw = 13 * mm
    lh = lw * logo.height / logo.width
    c.drawImage(str(TMP / "logo-blanc.png"), M, PH - 6.5 * mm - lh / 2, lw, lh, mask="auto")
    c.setFillColor(WHITE)
    c.setFont("Anton", 12)
    c.drawRightString(PW - M, PH - 8.6 * mm, "SPLASH PARTY  ·  PLAN DE COMMUNICATION")
    c.setStrokeColor(SAND)
    c.setLineWidth(1)
    c.line(M, 12 * mm, PW - M, 12 * mm)
    c.setFillColor(GREY)
    c.setFont("Helv", 8)
    c.drawString(M, 7.5 * mm, "Wellbeing Resort · Samedi 5 décembre 2026 · 07 47 79 95 07 / 05 66 92 33 91")
    c.drawRightString(PW - M, 7.5 * mm, f"{doc.page - 1}")
    c.restoreState()


def main():
    md = (HERE / "plan-de-communication.md").read_text(encoding="utf-8")
    title, story = parse(md)
    out = HERE / "plan-de-communication.pdf"
    doc = BaseDocTemplate(str(out), pagesize=A4, title="Splash Party : plan de communication",
                          author="ADOFE Communication", subject="Wellbeing Resort · Splash Party")
    doc.addPageTemplates([
        PageTemplate(id="cover", frames=[Frame(0, 0, PW, PH, id="c")], onPage=cover),
        PageTemplate(id="page", frames=[Frame(M, 16 * mm, PW - 2 * M, PH - 16 * mm - 20 * mm, id="p")],
                     onPage=page),
    ])
    doc.build([NextPageTemplate("page"), PageBreak()] + story)
    print("OK", out)


if __name__ == "__main__":
    main()
