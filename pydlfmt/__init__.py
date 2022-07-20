from dataclasses import dataclass
from reportlab.lib.styles import ParagraphStyle


import datetime
from decimal import ROUND_HALF_UP, Decimal

from dateutil.parser import parse
from reportlab.lib import colors, fonts, pagesizes, styles
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    SimpleDocTemplate,
    Paragraph,
    PageBreak,
    Spacer,
    PageTemplate,
    FrameBreak,
    Table,
    TableStyle,
    Frame,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus.flowables import KeepTogether
import reportlab.rl_config

from xlsxwriter import Workbook
from xlsxwriter.utility import xl_col_to_name


class DataFormatter:
    def __init__(self, data=None, filename=None, user_id=None):
        self.filename = filename
        self.user_id = user_id
        self.username = self.get_username()
        self.title = "Report Title"
        self.sub_title = ""

        self.columns = []
        self.data = data if data else []

        self.sections = []

        self.scalar_heading_column = 1

    def get_username(self):
        """
        override this method to build your username from the passed user id
        """
        return ""

    def to_pdf(
        self,
        headings=None,
        orientation="letter",
        top_margin=None,
        filename=None,
        default_tablestyle=None,
    ):
        if not headings:
            headings = []
            if self.title:
                headings.append(self.title)
            if self.sub_title:
                headings.append(self.sub_title)

        filename = (
            filename
            if filename
            else self.filename.replace("xlsx", "pdf")
            if self.filename
            else None
        )

        pr = PDFReport(
            data=self.data,
            sections=self.sections,
            headings=headings,
            orientation=orientation,
            scalar_heading_column=self.scalar_heading_column,
            filename=filename,
            username=self.username,
        )
        pr.columns = self.columns
        if top_margin:
            pr.top_margin = top_margin
        if default_tablestyle:
            pr.DEFAULT_TABLE_STYLE = default_tablestyle

        pr.build()

    def to_excel(
        self,
        filename=None,
        sheetname=None,
        format_table=None,
    ):

        filename = (
            filename
            if filename
            else self.filename.replace("pdf", "xlsx")
            if self.filename
            else None
        )

        xr = XLSXReport(
            data=self.data,
            sections=self.sections,
            sheetname=sheetname,
            filename=filename,
            format_table=format_table,
            username=self.username,
        )
        xr.columns = self.columns

        xr.build()


@dataclass
class ReportSection:
    header: str
    columns: list
    data: list
    pagebreak: bool = False
    tablestyle: list = None
    footer: str = None
    footer_style: ParagraphStyle = None
    format_table: bool = False


@dataclass
class Column:
    name: str
    heading: str = None
    font_size: float = 10
    bold: bool = False
    justify: str = "LEFT"
    scalar: str = ""
    decimal_positions: int = None
    currency: bool = False
    excel_formula: str = None
    datatype: str = "str"
    wrap: bool = False
    width: int = 10
    max_width: int = None
    paragraph_style = None
    include_commas: bool = False

    def __post_init__(self):
        self.heading = (
            self.heading.upper()
            if self.heading
            else self.name.replace("_", " ").upper()
        )
        self.justify = self.justify.upper()
        self.scalar = self.scalar.upper()

    def set_width(self, text_length):
        if not self.max_width or text_length > self.max_width:
            self.max_width = text_length if text_length > 10 else 10


@dataclass
class ExcelFormula:
    formula: str


class XLSXReport:
    def __init__(
        self,
        data=None,
        sections=None,
        headings=None,
        sheetname=None,
        filename="xlsx_report.xlsx",
        format_table=False,
        username=None,
        row_column_formats=None,
    ):
        self.data = data
        self.sections = sections
        self.sheetname = sheetname
        self.headings = headings
        self.filename = filename
        self.username = username
        self.format_table = format_table
        self.row_column_formats = row_column_formats

        if not self.headings:
            self.headings = ["XLSX Report"]

        self.columns = []

        self.workbook = None

    def setup_sheet(self):
        pass

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def build(self):
        self.setup_sheet()

        self.workbook = Workbook(self.filename)
        self.pre_build()

        if self.data and len(self.data) > 0:
            self.build_section(
                ReportSection(
                    header=self.sheetname,
                    columns=self.columns,
                    data=self.data,
                    format_table=self.format_table,
                )
            )
        else:
            for section in self.sections:
                self.build_section(section)

        self.post_build()

        self.workbook.close()

    def build_section(self, section):
        headings = [x.heading for x in section.columns]

        #  data, format_table=False, sheetname="Sheet1"
        if len(section.data) > 0:
            #  set default columns widths
            for column in section.columns:
                heading_length = len(column.heading) + 2
                if heading_length > column.width:
                    if column.max_width and heading_length >= column.max_width:
                        column.width = column.max_width
                    else:
                        if heading_length > column.width:
                            column.width = heading_length

            #  determine column widths
            for row in section.data:
                for column in section.columns:
                    if not column.excel_formula:
                        if isinstance(row, dict):
                            if column.name in row:
                                value = row[column.name]
                            else:
                                value = ""
                        else:
                            if column.name in row.__dict__:
                                value = row.__dict__[column.name]
                            else:
                                value = ""

                        if not isinstance(value, ExcelFormula):
                            value_length = len(str(value).strip())
                            if value_length > column.width:
                                if (
                                    column.max_width
                                    and value_length >= column.max_width
                                ):
                                    column.width = column.max_width
                                else:
                                    if value_length > column.width:
                                        column.width = value_length

                        if not column.max_width:
                            column.set_width(
                                max(len(x) for x in str(value).split("<br />"))
                            )

            ws = self.workbook.add_worksheet(
                name=section.header.replace("/", "-").replace(",", "")[:31]
                if section.header
                else "Sheet1"
            )

            #  write header row
            ws.write_row(
                row=0,
                col=0,
                data=headings,
            )

            for i, row in enumerate(section.data):
                height_rows = 1
                for j, column in enumerate(section.columns):
                    if isinstance(row, dict):
                        if column.name in row:
                            value = row[column.name]
                        else:
                            value = ""
                    else:
                        if column.name in row.__dict__:
                            value = row.__dict__[column.name]
                        else:
                            value = ""

                    cell_format = None
                    if isinstance(value, ExcelFormula):
                        value = (
                            value.formula.replace("?column-1", xl_col_to_name(j - 1))
                            .replace("?column-2", xl_col_to_name(j - 2))
                            .replace("?column+2", xl_col_to_name(j + 2))
                            .replace("?column", xl_col_to_name(j))
                        )
                        #
                        # value = (
                        #     value.formula.replace("?column-1", xl_col_to_name(j - 1))
                        #         .replace("?column-2", xl_col_to_name(j - 2))
                        #         .replace("?column+2", xl_col_to_name(j + 2))
                        #         .replace("?column", xl_col_to_name(j))
                        # )
                        #
                    elif column.excel_formula:
                        value = (
                            column.excel_formula.replace("?row", str(i + 2))
                            .replace("?column-1", xl_col_to_name(j - 1))
                            .replace("?column-2", xl_col_to_name(j - 2))
                            .replace("?column+2", xl_col_to_name(j + 2))
                            .replace("?column", xl_col_to_name(j))
                        )
                    else:
                        #  handle br in row for line breaks
                        if isinstance(value, str):
                            value = value.strip("\n")
                            num_rows = len(value.split("<br />"))
                            if num_rows > 1:
                                value = value.replace("<br />", "\n")
                                if num_rows > height_rows:
                                    height_rows = num_rows

                        if section.tablestyle:
                            for fmt in section.tablestyle:
                                attr = fmt[0]
                                from_cell = fmt[1]
                                to_cell = fmt[2]
                                modifier = fmt[3]
                                if from_cell == to_cell:
                                    if attr.lower() == "background":
                                        if from_cell[0] == j and from_cell[1] == i + 1:
                                            if from_cell == to_cell:
                                                if attr.lower() == "background":
                                                    if (
                                                        from_cell[0] == j
                                                        and from_cell[1] == i + 1
                                                    ):
                                                        f = self._get_column_format(
                                                            self.columns[j]
                                                        )
                                                        f[
                                                            "bg_color"
                                                        ] = modifier.hexval().replace(
                                                            "0x", "#"
                                                        )
                                                        cell_format = (
                                                            self.workbook.add_format(f)
                                                        )
                    if cell_format:
                        ws.write(i + 1, j, value, cell_format)
                    else:
                        ws.write(i + 1, j, value)

                if height_rows > 1:
                    ws.set_row(i + 1, 15.001 * height_rows)

            last_column_letter = xl_col_to_name(len(section.columns) - 1)

            if section.format_table:
                columns = []
                for i, column in enumerate(section.columns):
                    if column.scalar and column.scalar.upper() == "TOTAL":
                        columns.append(
                            {"header": column.heading, "total_function": "sum"}
                        )
                    elif column.scalar and column.scalar.upper() == "AVG":
                        columns.append(
                            {"header": column.heading, "total_function": "average"}
                        )
                    else:
                        columns.append({"header": column.heading})

                ws.add_table(
                    "A1:%s%s" % (last_column_letter, len(self.data) + 3),
                    {
                        "style": "Table Style Medium 15",
                        "total_row": 1,
                        "columns": columns,
                    },
                )
            else:
                for i, column in enumerate(section.columns):
                    if column.scalar == "TOTAL":
                        ws.write(
                            len(section.data) + 2,
                            i,
                            f"=SUM({xl_col_to_name(i)}2:{xl_col_to_name(i)}{len(section.data)+1})",
                        )
                    elif column.scalar == "AVG":
                        pass

            for i, column in enumerate(section.columns):
                ws.set_column(
                    i,
                    i,
                    column.max_width
                    if column.max_width and column.max_width < column.width
                    else column.width + 5,
                    self.workbook.add_format(self._get_column_format(column)),
                )

    @staticmethod
    def _get_column_format(column):
        f = dict(valign="top")

        if column.datatype.lower() in ["int", "integer"]:
            f["num_format"] = "#,##0"
        elif column.decimal_positions and column.decimal_positions > 0:
            f["num_format"] = "#,##0.000000000000"[: column.decimal_positions + 6]

        if column.datatype == "date":
            f["num_format"] = "mm/dd/yyyy"
        if column.datatype == "datetime":
            f["num_format"] = "mm/dd/yyyy HH:MM AM/PM"

        if column.justify == "CENTER":
            f["align"] = "center"
        elif column.justify == "RIGHT":
            f["align"] = "right"
        else:
            f["align"] = "left"

        if column.currency:
            if not column.decimal_positions:
                column.decimal_positions = 2
            f["num_format"] = "$ #,##0.000000000000"[: column.decimal_positions + 8]
            f["align"] = "right"

        if column.wrap:
            f["text_wrap"] = True

        return f


FORMAT_INT = "{0:,.0f}"


class PDFReport:
    def __init__(
        self,
        data=None,
        sections=None,
        headings=None,
        orientation="letter",
        scalar_heading_column=1,
        filename="pdf_report.pdf",
        username=None,
        date_format="%m/%d/%Y",
    ):
        self.headings = headings
        self.orientation = orientation
        self.data = data
        self.scalar_heading_column = scalar_heading_column
        self.filename = filename
        self.username = username
        self.sections = sections

        #  Report Setup
        reportlab.rl_config.warnOnMissingFontGlyphs = 0
        pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
        pdfmetrics.registerFont(TTFont("Arial Bold", "arialbd.ttf"))
        pdfmetrics.registerFont(TTFont("Arial Bold Italic", "arialbi.ttf"))
        pdfmetrics.registerFont(TTFont("Arial Italic", "ariali.ttf"))

        fonts.addMapping("Arial", 0, 0, "Arial")
        fonts.addMapping("Arial", 0, 1, "Arial Italic")
        fonts.addMapping("Arial", 1, 0, "Arial Bold")
        fonts.addMapping("Arial", 1, 1, "Arial Bold Italic")

        self.base_font = "Arial"
        self.bold_font = "Arial Bold"
        self.italic_font = "Arial Italic"
        self.bold_italic_font = "Arial Bold Italic"

        self.PAGE_HEIGHT = pagesizes.letter[1]
        self.PAGE_WIDTH = pagesizes.letter[0]

        self.DETAIL_STYLE = TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ("FONTNAME", (0, 0), (-1, -1), self.base_font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.transparent),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGNMENT", (0, 0), (-1, 0), "CENTER"),  # Center all Headings
                (
                    "ALIGNMENT",
                    (0, 1),
                    (-1, -1),
                    "LEFT",
                ),  # Left justify all remaining
                ("VALIGN", (0, 1), (-1, -1), "TOP"),
                ("VALIGN", (0, 0), (-1, 0), "BOTTOM"),
            ]
        )

        self.DEFAULT_TABLE_STYLE = [
            ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
            ("FONTNAME", (0, 0), (-1, -1), self.base_font),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BACKGROUND", (0, 0), (-1, 0), colors.transparent),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGNMENT", (0, 0), (-1, 0), "CENTER"),  # Center all Headings
            ("ALIGNMENT", (0, 1), (-1, -1), "LEFT"),  # Left justify all remaining
            ("VALIGN", (0, 1), (-1, -1), "TOP"),
            ("VALIGN", (0, 0), (-1, 0), "BOTTOM"),
        ]

        self.HEADER_STYLE = TableStyle(
            [
                # ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
                ("FONTNAME", (0, 0), (-1, -1), self.base_font),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTSIZE", (1, 1), (1, -1), 12),
                ("FONTSIZE", (1, 0), (1, 0), 16),
                ("BACKGROUND", (0, 0), (-1, 0), colors.transparent),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGNMENT", (0, 0), (0, -1), "LEFT"),
                ("ALIGNMENT", (1, 0), (1, -1), "CENTER"),
                ("ALIGNMENT", (2, 0), (2, -1), "RIGHT"),
                # ("BOTTOMPADDING", (0, 0), (-1, 0), 0.1 * inch),
                ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
            ]
        )

        self.style = styles.getSampleStyleSheet()
        self.styleN = self.style["Normal"]
        self.styleH = self.style["Heading1"]
        self.styleH2 = self.style["Heading2"]
        self.style_center = styles.getSampleStyleSheet()
        self.style_center_n = self.style_center["Normal"]
        self.style_center_n.alignment = TA_CENTER
        self.style_center_h = self.style_center["Heading1"]
        self.style_center_h.alignment = TA_CENTER
        self.style_right = styles.getSampleStyleSheet()
        self.style_right_n = self.style_right["Normal"]
        self.style_right_n.alignment = TA_RIGHT
        self.style_right_h = self.style_right["Heading1"]
        self.style_center_h.alignment = TA_RIGHT
        self.style_bullet = styles.getSampleStyleSheet()
        self.style_bullet_n = self.style_bullet["Bullet"]
        self.style_bullet_n.bulletFontName = "Symbol"
        self.style_bullet_n.leftIndent = 10

        self.report_story = []
        self.header_story = []

        self.row_heights = []
        self.report_period = ""

        if not self.headings:
            self.headings = ["QLF PDF Report"]

        self.report_story = []
        self.columns = []
        self.doc = None

        if self.orientation.upper() == "LANDSCAPE":
            self.pagesize = pagesizes.landscape(pagesizes.letter)
        else:
            self.pagesize = pagesizes.letter

        self.top_margin = 1.25 * inch + (0.5 * len(self.headings) - 1) * inch
        self.bottom_margin = 0.5 * inch
        self.left_margin = 0.5 * inch
        self.right_margin = 0.5 * inch

        self.date_format = date_format

    def setup_document(self):
        self.PAGE_HEIGHT = self.pagesize[1]
        self.PAGE_WIDTH = self.pagesize[0]

        self.doc = SimpleDocTemplate(
            self.filename,
            pagesize=self.pagesize,
            topMargin=self.top_margin,
            bottomMargin=self.bottom_margin,
            leftMargin=self.left_margin,
            rightMargin=self.right_margin,
        )

    def first_page(self, canvas, doc):
        """
        handle layout of the first page of the report

        NOTE: override this method to put custom headers in place

        Args:
            canvas (_type_): _description_
            doc (_type_): _description_
        """
        canvas.saveState()

        #  Print the headings
        style = self.styleN
        style.fontSize = 10

        header_data = []
        for i, heading in enumerate(self.headings):
            column_3 = ""
            if i == 0 and self.username:
                column_3 = f"Printed by: {self.username}"
            elif i == len(self.headings) - 1:
                column_3 = (
                    f"Printed: {datetime.date.today().strftime(self.date_format)}"
                )
            header_data.append(
                [
                    "",
                    heading,
                    column_3,
                ]
            )

        col_width = (self.PAGE_WIDTH - 1.0 * inch) / 3
        header_col_widths = (col_width, col_width, col_width)

        header_frame = Frame(
            x1=0.5 * inch,
            y1=self.PAGE_HEIGHT - 1.5 * inch,
            width=self.PAGE_WIDTH - 1.0 * inch,
            height=1 * inch,
        )
        header_table = Table(header_data, header_col_widths)
        header_table.setStyle(self.HEADER_STYLE)
        self.header_story.append(header_table)
        header_frame.addFromList(self.header_story, canvas)

        #  Print the page number
        canvas.setFont("Arial", 8)
        canvas.drawRightString(
            self.PAGE_WIDTH - 0.5 * inch, 0.4 * inch, "Page %d" % doc.page
        )
        canvas.restoreState()

    def subsequent_pages(self, canvas, doc):
        self.first_page(canvas, doc)

    def pre_build(self):
        pass

    def post_build(self):
        pass

    def build(self):
        self.setup_document()

        self.pre_build()

        if self.data and len(self.data) > 0:
            self.build_section(
                ReportSection(header="", columns=self.columns, data=self.data)
            )
        else:
            for section in self.sections:
                self.build_section(section)

        self.post_build()

        self.doc.build(
            self.report_story,
            onFirstPage=self.first_page,
            onLaterPages=self.subsequent_pages,
        )

    def build_section(self, section):
        if section.header and section.header != "":
            self.report_story.append(Paragraph(section.header, style=self.styleH2))
        else:
            self.report_story.append(Spacer(1, 0.25 * inch))

        for column in section.columns:
            if column.excel_formula and len(column.excel_formula) > 0:
                section.columns.remove(column)

        for col_number, column in enumerate(section.columns):
            #  add alignments from column defaults
            if column.justify != "LEFT":
                self.DEFAULT_TABLE_STYLE.append(
                    ("ALIGNMENT", (col_number, 1), (col_number, -1), column.justify)
                )
            if column.font_size and column.font_size > 0:
                self.DEFAULT_TABLE_STYLE.append(
                    (
                        "FONTSIZE",
                        (col_number, 1),
                        (col_number, -1),
                        column.font_size,
                    )
                )
            if column.bold:
                self.DEFAULT_TABLE_STYLE.append(
                    ("FONTNAME", (col_number, 1), (col_number, -1), self.bold_font)
                )

        report_data = [[x.heading for x in section.columns]]
        scalars = dict(TOTAL=dict(), AVG=dict(), COUNT=dict())
        for row in section.data:
            rr = []
            for column in section.columns:
                column_style = (
                    column.paragraph_style if column.paragraph_style else self.styleN
                )
                if column.justify == "CENTER":
                    column_style = self.style_center_n
                elif column.justify == "RIGHT" or column.currency:
                    column_style = self.style_right_n

                if isinstance(row, dict):
                    value = row[column.name]
                else:
                    value = row.__dict__[column.name]

                if value:
                    if column.datatype.lower() in ["int", "integer"]:
                        scalar_rounding = "0"
                        value = Decimal(value).quantize(
                            Decimal(scalar_rounding), rounding=ROUND_HALF_UP
                        )
                        if column.include_commas:
                            value = FORMAT_INT.format(value)
                    elif column.datatype.lower() == "date":
                        if not isinstance(value, datetime.date):
                            value = parse(value).date()
                        value = value.strftime("%m/%d/%Y")
                    elif column.datatype.lower() == "datetime":
                        if not isinstance(value, datetime.datetime):
                            value = parse(value)
                        value = value.strftime("%m/%d/%Y %I:%M%p")
                    elif column.decimal_positions:
                        scalar_rounding = "0.0000000000"[: column.decimal_positions + 2]
                        value = Decimal(value).quantize(
                            Decimal(scalar_rounding), rounding=ROUND_HALF_UP
                        )
                        if column.include_commas:
                            fmt = "{0:,.%sf}" % column.decimal_positions
                            value = fmt.format(value)
                    column_style.fontSize = column.font_size
                    display_value = value
                    if column.currency:
                        display_value = f"${value}"
                    rr.append(Paragraph(str(display_value), style=column_style))
                else:
                    rr.append("")
                string_value = str(value)
                x = max(len(x) for x in string_value.split("<br />"))
                # column.set_width(
                #     len(str(max(len(x) for x in string_value.split("<br />"))))
                # )
                column.set_width(max(len(x) for x in string_value.split("<br />")))
                for scalar in scalars:
                    if column.scalar == scalar:
                        if column.name not in scalars[scalar]:
                            scalars[scalar][column.name] = 0
                        if value:
                            scalar_rounding = "0.00"
                            if column.datatype.lower() in ["int", "integer"]:
                                scalar_rounding = "0"
                            if isinstance(value, str):
                                value = value.replace(",", "")
                            if column.decimal_positions:
                                scalar_rounding = "0.0000000000"[
                                    : column.decimal_positions + 2
                                ]
                            scalars[scalar][column.name] += Decimal(value).quantize(
                                Decimal(scalar_rounding),
                                rounding=ROUND_HALF_UP,
                            )

            report_data.append(rr)

        data_rows = len(report_data)
        for scalar in sorted(scalars):
            scalar_label_written = False
            if len(scalars[scalar]) > 0:
                #  add summary row:
                rr = []
                for column_number, column in enumerate(section.columns):
                    if column.name in scalars[scalar]:
                        if scalar == "TOTAL":
                            if column.include_commas:
                                if column.datatype.lower() in ["int", "integer"]:
                                    scalars[scalar][column.name] = FORMAT_INT.format(
                                        scalars[scalar][column.name]
                                    )
                                elif column.decimal_positions:
                                    fmt = "{0:,.%sf}" % column.decimal_positions
                                    scalars[scalar][column.name] = fmt.format(
                                        scalars[scalar][column.name]
                                    )
                            rr.append(scalars[scalar][column.name])
                        elif scalar == "AVG":
                            rr.append(
                                Decimal(
                                    scalars[scalar][column.name] / data_rows
                                ).quantize(Decimal("0.00"))
                            )
                        elif scalar == "COUNT":
                            rr.append(Decimal(data_rows).quantize(Decimal("0")))
                    else:
                        if not scalar_label_written and self.scalar_heading_column == (
                            column_number + 1
                        ):
                            column_style = (
                                column.paragraph_style
                                if column.paragraph_style
                                else self.styleN
                            )
                            rr.append(
                                Paragraph(
                                    f"{scalar} {section.header}", style=column_style
                                )
                            )
                            scalar_label_written = True
                        else:
                            rr.append("")
                report_data.append(rr)

        if len(self.row_heights) > 0:
            data_table = Table(
                report_data,
                colWidths=self.get_column_widths(section.columns),
                repeatRows=1,
                rowHeights=self.row_heights,
            )
        else:
            data_table = Table(
                report_data,
                colWidths=self.get_column_widths(section.columns),
                repeatRows=1,
            )

        data_table.setStyle(
            TableStyle(
                section.tablestyle if section.tablestyle else self.DEFAULT_TABLE_STYLE
            )
        )
        self.report_story.append(data_table)

        if section.footer and section.footer != "":
            self.report_story.append(Spacer(1, 0.1 * inch))
            self.report_story.append(
                Paragraph(
                    section.footer,
                    style=section.footer_style if section.footer_style else self.styleN,
                )
            )
        else:
            self.report_story.append(Spacer(1, 0.25 * inch))

        if section.pagebreak:
            self.report_story.append(PageBreak())

    def get_column_widths(self, columns=None):
        if not columns:
            columns = self.columns

        column_widths = []

        #  get total width
        total_width = sum([x.max_width for x in columns])
        page_width = self.PAGE_WIDTH - self.left_margin - self.right_margin

        for column in columns:
            column_widths.append(page_width * column.max_width / total_width)

        return column_widths
