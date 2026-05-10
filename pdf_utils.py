from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame
from reportlab.platypus.flowables import Flowable
import os

# Color Palette
C_BG       = colors.HexColor('#0D1117')
C_PRIMARY  = colors.HexColor('#1F6FEB')
C_ACCENT   = colors.HexColor('#3FB950')
C_WARN     = colors.HexColor('#F78166')
C_GOLD     = colors.HexColor('#E3B341')
C_WHITE    = colors.HexColor('#E6EDF3')
C_MUTED    = colors.HexColor('#8B949E')
C_CARD     = colors.HexColor('#161B22')
C_BORDER   = colors.HexColor('#30363D')
C_PURPLE   = colors.HexColor('#BC8CFF')

PAGE_W, PAGE_H = A4

def make_styles(accent=None):
    if accent is None:
        accent = C_PRIMARY
    styles = getSampleStyleSheet()
    custom = {}

    custom['cover_title'] = ParagraphStyle('cover_title',
        fontName='Helvetica-Bold', fontSize=34, textColor=C_WHITE,
        alignment=TA_CENTER, spaceAfter=8, leading=40)

    custom['cover_sub'] = ParagraphStyle('cover_sub',
        fontName='Helvetica', fontSize=15, textColor=C_MUTED,
        alignment=TA_CENTER, spaceAfter=6, leading=20)

    custom['cover_tag'] = ParagraphStyle('cover_tag',
        fontName='Helvetica-Bold', fontSize=11, textColor=accent,
        alignment=TA_CENTER, spaceAfter=4)

    custom['h1'] = ParagraphStyle('h1',
        fontName='Helvetica-Bold', fontSize=20, textColor=accent,
        spaceBefore=18, spaceAfter=6, leading=24, borderPadding=(0,0,4,0))

    custom['h2'] = ParagraphStyle('h2',
        fontName='Helvetica-Bold', fontSize=15, textColor=C_WHITE,
        spaceBefore=14, spaceAfter=4, leading=18)

    custom['h3'] = ParagraphStyle('h3',
        fontName='Helvetica-Bold', fontSize=12, textColor=C_GOLD,
        spaceBefore=10, spaceAfter=3, leading=15)

    custom['h4'] = ParagraphStyle('h4',
        fontName='Helvetica-Bold', fontSize=10, textColor=C_PURPLE,
        spaceBefore=6, spaceAfter=2, leading=13)

    custom['body'] = ParagraphStyle('body',
        fontName='Helvetica', fontSize=9, textColor=C_WHITE,
        spaceBefore=2, spaceAfter=3, leading=14, alignment=TA_JUSTIFY)

    custom['body_sm'] = ParagraphStyle('body_sm',
        fontName='Helvetica', fontSize=8, textColor=C_WHITE,
        spaceBefore=1, spaceAfter=2, leading=12)

    custom['bullet'] = ParagraphStyle('bullet',
        fontName='Helvetica', fontSize=9, textColor=C_WHITE,
        spaceBefore=1, spaceAfter=1, leading=13,
        leftIndent=14, firstLineIndent=-10)

    custom['bullet2'] = ParagraphStyle('bullet2',
        fontName='Helvetica', fontSize=8.5, textColor=C_MUTED,
        spaceBefore=1, spaceAfter=1, leading=12,
        leftIndent=24, firstLineIndent=-10)

    custom['code'] = ParagraphStyle('code',
        fontName='Courier', fontSize=8, textColor=C_ACCENT,
        spaceBefore=2, spaceAfter=2, leading=11,
        leftIndent=8, backColor=C_CARD,
        borderColor=C_BORDER, borderWidth=0.5,
        borderPadding=5)

    custom['code_sm'] = ParagraphStyle('code_sm',
        fontName='Courier', fontSize=7.5, textColor=C_ACCENT,
        spaceBefore=1, spaceAfter=1, leading=10,
        leftIndent=8, backColor=C_CARD,
        borderColor=C_BORDER, borderWidth=0.5, borderPadding=4)

    custom['warn_box'] = ParagraphStyle('warn_box',
        fontName='Helvetica', fontSize=9, textColor=C_WARN,
        spaceBefore=3, spaceAfter=3, leading=13,
        backColor=colors.HexColor('#2D1B1B'),
        borderColor=C_WARN, borderWidth=1, borderPadding=6,
        leftIndent=8)

    custom['tip_box'] = ParagraphStyle('tip_box',
        fontName='Helvetica', fontSize=9, textColor=C_ACCENT,
        spaceBefore=3, spaceAfter=3, leading=13,
        backColor=colors.HexColor('#0D2818'),
        borderColor=C_ACCENT, borderWidth=1, borderPadding=6,
        leftIndent=8)

    custom['info_box'] = ParagraphStyle('info_box',
        fontName='Helvetica', fontSize=9, textColor=C_PRIMARY,
        spaceBefore=3, spaceAfter=3, leading=13,
        backColor=colors.HexColor('#0D1F3C'),
        borderColor=C_PRIMARY, borderWidth=1, borderPadding=6,
        leftIndent=8)

    custom['muted'] = ParagraphStyle('muted',
        fontName='Helvetica', fontSize=8, textColor=C_MUTED,
        spaceBefore=1, spaceAfter=1, leading=11)

    custom['tag_green'] = ParagraphStyle('tag_green',
        fontName='Helvetica-Bold', fontSize=7.5, textColor=C_ACCENT,
        alignment=TA_CENTER)

    custom['tag_red'] = ParagraphStyle('tag_red',
        fontName='Helvetica-Bold', fontSize=7.5, textColor=C_WARN,
        alignment=TA_CENTER)

    custom['tag_blue'] = ParagraphStyle('tag_blue',
        fontName='Helvetica-Bold', fontSize=7.5, textColor=C_PRIMARY,
        alignment=TA_CENTER)

    custom['toc'] = ParagraphStyle('toc',
        fontName='Helvetica', fontSize=10, textColor=C_WHITE,
        spaceBefore=2, spaceAfter=2, leading=14, leftIndent=10)

    custom['toc_h'] = ParagraphStyle('toc_h',
        fontName='Helvetica-Bold', fontSize=11, textColor=accent,
        spaceBefore=6, spaceAfter=2, leading=14)

    return custom


def dark_table_style(header_color=None):
    if header_color is None:
        header_color = C_PRIMARY
    return TableStyle([
        ('BACKGROUND',    (0,0), (-1,0),  header_color),
        ('TEXTCOLOR',     (0,0), (-1,0),  C_WHITE),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  8.5),
        ('ALIGN',         (0,0), (-1,0),  'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,0),  6),
        ('TOPPADDING',    (0,0), (-1,0),  6),
        ('BACKGROUND',    (0,1), (-1,-1), C_CARD),
        ('TEXTCOLOR',     (0,1), (-1,-1), C_WHITE),
        ('FONTNAME',      (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE',      (0,1), (-1,-1), 8),
        ('ALIGN',         (0,1), (-1,-1), 'LEFT'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS',(0,1), (-1,-1), [C_CARD, colors.HexColor('#1C2128')]),
        ('GRID',          (0,0), (-1,-1), 0.5, C_BORDER),
        ('TOPPADDING',    (0,1), (-1,-1), 4),
        ('BOTTOMPADDING', (0,1), (-1,-1), 4),
        ('LEFTPADDING',   (0,0), (-1,-1), 6),
        ('RIGHTPADDING',  (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS',(0,1),(-1,-1), [C_CARD, colors.HexColor('#1C2128')]),
    ])


def build_doc(path, story, title='', accent=C_PRIMARY):
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(C_BG)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        # Header bar
        canvas.setFillColor(accent)
        canvas.rect(0, PAGE_H - 22*mm, PAGE_W, 3, fill=1, stroke=0)
        # Footer
        canvas.setFillColor(C_BORDER)
        canvas.rect(0, 14*mm, PAGE_W, 0.5, fill=1, stroke=0)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(C_MUTED)
        canvas.drawString(20*mm, 10*mm, title)
        canvas.drawRightString(PAGE_W - 20*mm, 10*mm, f'Page {doc.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=26*mm, bottomMargin=22*mm,
        title=title,
    )
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def hr(color=C_BORDER, thickness=0.5, space=4):
    return HRFlowable(width='100%', thickness=thickness, color=color,
                      spaceAfter=space, spaceBefore=space)


def tag(text, color=C_ACCENT):
    return f'<font color="{color.hexval() if hasattr(color,"hexval") else color}">[{text}]</font>'


def b(text):
    return f'<b>{text}</b>'


def color_text(text, color):
    hex_c = color.hexval() if hasattr(color, 'hexval') else str(color)
    return f'<font color="{hex_c}">{text}</font>'
