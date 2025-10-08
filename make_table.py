import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus import KeepTogether
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import json
from class_name_reshape import class_name_reshape
from env import PDF_NAME, API_JSON, CLASS_CODE
from reportlab.pdfgen import canvas

# 註冊字型，否則會變框框
pdfmetrics.registerFont(TTFont("MSJH", "C:/Windows/Fonts/msjh.ttc"))
pdfmetrics.registerFont(TTFont("MSJH-Bold", "C:/Windows/Fonts/msjhbd.ttc"))

# 樣式
styles = getSampleStyleSheet()
style_normal = ParagraphStyle("Normal", fontName="MSJH", fontSize=10, leading=12)
style_light = ParagraphStyle("Light", fontName="MSJH", fontSize=10, leading=12, textColor=colors.gray)
style_bold = ParagraphStyle("Bold", fontName="MSJH-Bold", fontSize=9, leading=12)

def add_page_title(c: canvas.Canvas, doc):
    c.saveState()
    title_text = CLASS_CODE + " 課表"
    style_title = ParagraphStyle(
        name="PageTitle",
        fontName="MSJH-Bold",
        fontSize=14,
        leading=16,
        alignment=1
    )
    p = Paragraph(title_text, style_title)
    w, h = p.wrap(A4[0]-40, 50)  # 寬、高
    p.drawOn(c, 20, A4[1]-h-10)  # x, y
    c.restoreState()

def make_table(schedule):
    schedule_ = schedule["data"]["scheduleList"]
    for class_ in schedule_:
        teacher_list = class_.get("teacherList", [])
        class_["teacher"] = teacher_list[0]["nickname"] if teacher_list else ""
    df = pd.DataFrame(schedule_)
    df = df[["name", "classStartTime", "classEndTime", "date", "interval", "classRoomName", "teacher"]]
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.to_period("W-SUN")
    # 修短時間格式
    df["classStartTime"] = pd.to_datetime(df["classStartTime"], format="%H:%M:%S").dt.strftime("%H:%M")
    df["classEndTime"]   = pd.to_datetime(df["classEndTime"], format="%H:%M:%S").dt.strftime("%H:%M")

    # -------------------
    # 分割課程名稱
    df["name"] = df["name"].map(class_name_reshape(schedule))

    # -----------------------
    # 3. 建立 PDF
    # -----------------------
    pdf_file = PDF_NAME
    # 版面設定
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=20,   # 左邊界
        rightMargin=20,  # 右邊界
        topMargin=30,    # 上邊界
        bottomMargin=20  # 下邊界
    )
    elements = []



    # -----------------------
    # 4. 生成每週表格
    # -----------------------
    interval_map = {
        "Day": "上午",
        "Evening": "下午",
        "Night": "晚上"
    }
    interval_order = ["上午", "下午", "晚上"]

    for i, (week_idx, week_data) in enumerate(df.groupby("week"), start=1):
        week_start = (week_data["date"].min() - pd.offsets.Week(weekday=6)).normalize()
        week_dates = pd.date_range(start=week_start, periods=7)
        week_data["interval"] = week_data["interval"].map(interval_map)

        # 分離課程名稱與其他資訊
        week_data["info_name"] = week_data["name"]
        week_data["info_detail"] = (
            "(" + week_data["classStartTime"] + "-" + week_data["classEndTime"] + ")"
            + "<br/>" + week_data["teacher"] + "  @" + week_data["classRoomName"]
        )

        # 建立兩個 Pivot
        pivot_name = week_data.pivot_table(
            index="interval", columns="date", values="info_name",
            aggfunc=lambda x: "<br/><br/>".join(x)
        ).reindex(interval_order).fillna("")

        pivot_detail = week_data.pivot_table(
            index="interval", columns="date", values="info_detail",
            aggfunc=lambda x: "<br/><br/>".join(x)
        ).reindex(interval_order).fillna("")

        # 建立表格資料（兩層）
        table_data = [[f"第{i}週"] + [d.strftime("%m/%d (%a)") for d in week_dates]]

        for row_label in interval_order:
            # 第一列：課程名稱（粗體）
            row_name = [row_label]
            for d in week_dates:
                text = pivot_name.loc[row_label].get(d, "") if d in pivot_name.columns else ""
                row_name.append(Paragraph(text, style_bold))
            table_data.append(row_name)

            # 第二列：詳細資訊（時間、地點、老師）
            row_detail = [""]
            for d in week_dates:
                text = pivot_detail.loc[row_label].get(d, "") if d in pivot_detail.columns else ""
                row_detail.append(Paragraph(text, style_light))
            table_data.append(row_detail)

        # 建立表格
        table = Table(
            table_data,
            colWidths=[35] + [60] + [75]*6,
            rowHeights=[20] + [40, 35]*3  # 每組「上午」佔兩列
        )

        # 設對齊樣式
        ts = TableStyle([           
            ("FONTNAME", (0,0), (-1,-1), "MSJH"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (0,0), (-1,0), "CENTER"),
            ("ALIGN", (0,1), (-1,-1), "LEFT"),
            ("VALIGN", (1,1), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (-1,0), colors.lightblue),   # 日期列底色
            ("BACKGROUND", (0,1), (0,-1), colors.azure),   # 時段底色
            ("BACKGROUND", (1,1), (1,-1), colors.lavenderblush),   # 週日底色
            ("BACKGROUND", (-1,1), (-1,-1), colors.honeydew),   # 週六底色
        ])
        
        # 劃格線

        # 標題列 (日期列) 下方線 + 上午/下午/晚上 上方線
        ts.add("LINEBELOW", (0,0), (-1,0), 1, colors.black)  # 日期列底線

        # 每組課程名稱與課程資訊間的線 (細線灰色)
        for idx, _ in enumerate(interval_order):
            row_name = 1 + idx*2        # 課程名稱列
            row_detail = row_name + 1   # 課程資訊列
            ts.add("LINEBELOW", (0, row_name), (-1, row_name), 0.5, colors.lightgrey)

        # 每天間的細線 (橫向)
        for idx, _ in enumerate(interval_order):
            row_detail = 1 + idx*2 + 1
            ts.add("LINEBELOW", (0, row_detail), (-1, row_detail), 0.7, colors.gray)

        # 合併「上午/下午/晚上」欄位上下兩列
        for idx, _ in enumerate(interval_order):
            row_start = 1 + idx*2
            row_end = row_start + 1
            ts.add("SPAN", (0, row_start), (0, row_end))
        
        # 每天間的豎線 (從第一列資料開始，不含最左欄)
        for col_idx in range(2, 2 + 7 - 1):  # 第一欄是上午/下午/晚上，日期列 7 天
            ts.add("LINEBEFORE", (0, 0), (-1, -1), 1, colors.black)
        
        # 畫外框
        ts.add("BOX", (0,0), (-1,-1), 1, colors.black)
        table.setStyle(ts)

        elements.append(KeepTogether(table))
        elements.append(Spacer(1, 10))

    # -----------------------
    # 5. 輸出 PDF
    # -----------------------

    doc.build(elements, onFirstPage=add_page_title, onLaterPages=add_page_title)

    print(f"已產生 PDF: {pdf_file}")

if __name__ == "__main__":
    with open(API_JSON, "r", encoding="utf-8") as file:
        schedule = json.load(file)
    make_table(schedule)
