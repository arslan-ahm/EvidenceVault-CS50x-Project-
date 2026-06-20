from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def build_case_report_pdf(case_title: str, case_description: str | None, evidence_rows: list[dict], timeline_rows: list[dict]) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 48

    def write_line(text: str, indent: int = 0, leading: int = 16) -> None:
        nonlocal y
        if y < 72:
            pdf.showPage()
            y = height - 48
        pdf.drawString(48 + indent, y, text[:120])
        y -= leading

    pdf.setTitle(case_title)
    pdf.setFont("Helvetica-Bold", 18)
    write_line(case_title)
    pdf.setFont("Helvetica", 11)
    if case_description:
        write_line(case_description)
    y -= 12
    pdf.setFont("Helvetica-Bold", 14)
    write_line("Evidence")
    pdf.setFont("Helvetica", 10)
    for row in evidence_rows:
        write_line(f"- {row['file_name']} ({row['file_type']})", indent=12)
    y -= 10
    pdf.setFont("Helvetica-Bold", 14)
    write_line("Timeline")
    pdf.setFont("Helvetica", 10)
    for row in timeline_rows:
        event_date = row.get("event_date") or "Undated"
        write_line(f"- {event_date}: {row['event_text']}", indent=12)

    pdf.save()
    return buffer.getvalue()
