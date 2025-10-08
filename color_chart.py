from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# 取得所有顏色名稱
color_names = [c for c in dir(colors) if not c.startswith("_") and isinstance(getattr(colors, c), colors.Color)]
color_list = [(name, getattr(colors, name)) for name in color_names]

# 樣式設定
styles = getSampleStyleSheet()
style_title = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=16, leading=20, alignment=1)
style_normal = ParagraphStyle("Normal", fontName="Helvetica", fontSize=10, leading=12)

# 建立表格資料
table_data = [["Color", "Name"]]
for name, color in color_list:
    table_data.append(["", Paragraph(name, style_normal)])

# 建立 PDF 文件
doc = SimpleDocTemplate("color_chart.pdf", pagesize=A4, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)

# 建立表格
table = Table(table_data, colWidths=[150, 250], repeatRows=1)

# 設定表格樣式
table_style = TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
    ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
    ("TEXTCOLOR", (1, 1), (-1, -1), colors.black),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
])

# 為每一行加上背景色塊
for i, (_, color) in enumerate(color_list, start=1):
    table_style.add("BACKGROUND", (0, i), (0, i), color)

table.setStyle(table_style)

# 輸出 PDF
elements = [
    Paragraph("ReportLab Colors Chart", style_title),
    Spacer(1, 12),
    table
]
doc.build(elements)
