"""
billing/utils.py

Utilities for:
  - Generating a professional PDF payment receipt (reportlab)
  - Saving the PDF to MEDIA_ROOT/invoices/
  - Emailing the receipt to the candidate (with PDF attachment)
"""
import io
import os
from datetime import date, datetime

from django.conf import settings
from django.core.mail import EmailMessage


# ── PDF Generation ────────────────────────────────────────────────────────────

def _get_reportlab():
    """Lazy import so the app doesn't crash if reportlab isn't installed."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )
    return (
        A4, colors, mm, getSampleStyleSheet, ParagraphStyle,
        TA_CENTER, TA_RIGHT, TA_LEFT,
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )


def generate_receipt_pdf(payment, invoice=None) -> bytes:
    """
    Build a PDF payment receipt and return it as raw bytes.

    Args:
        payment:  billing.models.Payment instance
        invoice:  billing.models.Invoice instance (optional, for richer detail)

    Returns:
        bytes — the PDF content, or b'' on failure.
    """
    try:
        (
            A4, colors, mm, getSampleStyleSheet, ParagraphStyle,
            TA_CENTER, TA_RIGHT, TA_LEFT,
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
        ) = _get_reportlab()
    except ImportError:
        return b''

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=20 * mm, bottomMargin=20 * mm,
    )

    styles   = getSampleStyleSheet()
    BRAND    = colors.HexColor('#1E3A5F')   # Hyrind dark blue
    LIGHT_BG = colors.HexColor('#F4F7FB')
    GRAY     = colors.HexColor('#6B7280')

    def style(name, **kwargs):
        s = styles[name].clone(name + '_custom')
        for k, v in kwargs.items():
            setattr(s, k, v)
        return s

    candidate_user    = payment.candidate.user
    candidate_profile = getattr(candidate_user, 'profile', None)
    candidate_name    = (
        candidate_profile.full_name if candidate_profile else candidate_user.email
    )

    invoice_number    = invoice.invoice_number if invoice else f'REC-{str(payment.id)[:8].upper()}'
    payment_date_str  = str(payment.payment_date or date.today())
    generated_at      = datetime.now().strftime('%Y-%m-%d %H:%M')

    story = []

    # ── Header bar ────────────────────────────────────────────────────────
    header_table = Table(
        [[
            Paragraph('<font color="white"><b>HYRIND</b></font>',
                      style('Normal', fontSize=22, textColor=colors.white)),
            Paragraph('<font color="white">PAYMENT RECEIPT</font>',
                      style('Normal', fontSize=14, textColor=colors.white, alignment=TA_RIGHT)),
        ]],
        colWidths=[90 * mm, 80 * mm],
    )
    header_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), BRAND),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING',  (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (0, 0),   8),
        ('RIGHTPADDING', (-1, 0), (-1, 0), 8),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6 * mm))

    # ── Invoice meta ──────────────────────────────────────────────────────
    meta_data = [
        ['Receipt / Invoice No.', invoice_number],
        ['Date',                  payment_date_str],
        ['Generated',             generated_at],
        ['Status',                payment.status.upper()],
    ]
    meta_table = Table(meta_data, colWidths=[55 * mm, 115 * mm])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (0, -1), LIGHT_BG),
        ('TEXTCOLOR',   (0, 0), (0, -1), GRAY),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#D1D5DB')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6 * mm))

    # ── Bill to ───────────────────────────────────────────────────────────
    story.append(Paragraph('Bill To:', style('Normal', textColor=GRAY, fontSize=9)))
    story.append(Paragraph(f'<b>{candidate_name}</b>', style('Normal', fontSize=11)))
    story.append(Paragraph(candidate_user.email,       style('Normal', fontSize=10)))
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#D1D5DB')))
    story.append(Spacer(1, 4 * mm))

    # ── Line items ────────────────────────────────────────────────────────
    line_item_rows = [
        [
            Paragraph('<b>Description</b>',           style('Normal', fontSize=9)),
            Paragraph('<b>Type</b>',                   style('Normal', fontSize=9)),
            Paragraph('<b>Amount</b>',                 style('Normal', fontSize=9, alignment=TA_RIGHT)),
        ]
    ]

    # If linked to a PaymentLineItem, show its charge_name
    if payment.line_item:
        li = payment.line_item
        line_item_rows.append([
            Paragraph(li.charge_name,                  style('Normal', fontSize=10)),
            Paragraph(li.get_charge_type_display(),    style('Normal', fontSize=10)),
            Paragraph(f'{li.currency} {li.amount:,.2f}',
                      style('Normal', fontSize=10, alignment=TA_RIGHT)),
        ])
    else:
        line_item_rows.append([
            Paragraph(payment.payment_type.replace('_', ' ').title(), style('Normal', fontSize=10)),
            Paragraph('Payment',                       style('Normal', fontSize=10)),
            Paragraph(f'{payment.currency} {payment.amount:,.2f}',
                      style('Normal', fontSize=10, alignment=TA_RIGHT)),
        ])

    items_table = Table(line_item_rows, colWidths=[90 * mm, 45 * mm, 35 * mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), BRAND),
        ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('LINEBELOW',     (0, 1), (-1, -1), 0.3, colors.HexColor('#D1D5DB')),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # ── Totals ────────────────────────────────────────────────────────────
    total_table = Table(
        [['', 'Total Paid', f'{payment.currency} {payment.amount:,.2f}']],
        colWidths=[90 * mm, 45 * mm, 35 * mm],
    )
    total_table.setStyle(TableStyle([
        ('BACKGROUND',  (1, 0), (-1, 0), BRAND),
        ('TEXTCOLOR',   (1, 0), (-1, 0), colors.white),
        ('FONTNAME',    (1, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',    (1, 0), (-1, 0), 10),
        ('ALIGN',       (2, 0), (2, 0),  'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (1, 0), (-1, 0), 8),
        ('RIGHTPADDING',  (2, 0), (2, 0),  8),
    ]))
    story.append(total_table)
    story.append(Spacer(1, 6 * mm))

    # ── Transaction reference ─────────────────────────────────────────────
    if payment.transaction_ref:
        story.append(Paragraph(
            f'Transaction Reference: <b>{payment.transaction_ref}</b>',
            style('Normal', textColor=GRAY, fontSize=9),
        ))
        story.append(Spacer(1, 3 * mm))

    # ── Notes ─────────────────────────────────────────────────────────────
    if payment.notes:
        story.append(Paragraph(f'Notes: {payment.notes}', style('Normal', textColor=GRAY, fontSize=9)))
        story.append(Spacer(1, 3 * mm))

    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#D1D5DB')))
    story.append(Spacer(1, 4 * mm))

    # ── Footer ────────────────────────────────────────────────────────────
    story.append(Paragraph(
        'Thank you for your payment. This receipt was automatically generated by the Hyrind Platform.',
        style('Normal', textColor=GRAY, fontSize=8, alignment=TA_CENTER),
    ))
    story.append(Paragraph(
        'For support, contact: support@hyrind.com',
        style('Normal', textColor=GRAY, fontSize=8, alignment=TA_CENTER),
    ))

    doc.build(story)
    return buffer.getvalue()


# ── PDF save to disk ──────────────────────────────────────────────────────────

def save_receipt_pdf(payment, invoice=None) -> str | None:
    """
    Generate a PDF receipt and persist it to MEDIA_ROOT/invoices/.

    Returns the relative path as stored in Invoice.pdf_path, e.g.
    'invoices/INV-2026-000001.pdf', or None on failure.
    """
    pdf_bytes = generate_receipt_pdf(payment, invoice)
    if not pdf_bytes:
        return None

    filename    = f'REC-{str(payment.id)[:8].upper()}.pdf'
    if invoice and invoice.invoice_number:
        filename = f'{invoice.invoice_number}.pdf'

    rel_path    = os.path.join('invoices', filename)
    abs_dir     = os.path.join(settings.MEDIA_ROOT, 'invoices')
    os.makedirs(abs_dir, exist_ok=True)
    abs_path    = os.path.join(abs_dir, filename)

    with open(abs_path, 'wb') as f:
        f.write(pdf_bytes)

    return rel_path


# ── Email with PDF attachment ─────────────────────────────────────────────────

def send_payment_receipt_email(payment, invoice=None):
    """
    Email a payment receipt PDF to the candidate.
    Logs the result via notifications.utils.create_notification.
    """
    try:
        candidate_user = payment.candidate.user
        profile        = getattr(candidate_user, 'profile', None)
        candidate_name = profile.full_name if profile else candidate_user.email
        invoice_number = invoice.invoice_number if invoice else f'REC-{str(payment.id)[:8].upper()}'

        pdf_bytes = generate_receipt_pdf(payment, invoice)

        subject = f'Payment Receipt {invoice_number} — Hyrind'
        body_html = f"""
<p>Hi <strong>{candidate_name}</strong>,</p>
<p>Thank you! We have successfully received your payment of
<strong>{payment.currency} {payment.amount:,.2f}</strong>
on {payment.payment_date or 'today'}.</p>
<p>Please find your payment receipt attached to this email.</p>
<p>
  <b>Receipt No.:</b> {invoice_number}<br>
  <b>Amount:</b> {payment.currency} {payment.amount:,.2f}<br>
  <b>Status:</b> {payment.status.upper()}
</p>
<p>For any questions, reply to this email or contact <a href="mailto:support@hyrind.com">support@hyrind.com</a>.</p>
<p>— The Hyrind Team</p>
"""
        email = EmailMessage(
            subject=subject,
            body=body_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[candidate_user.email],
        )
        email.content_subtype = 'html'

        if pdf_bytes:
            email.attach(f'{invoice_number}.pdf', pdf_bytes, 'application/pdf')

        email.send(fail_silently=True)

        # In-app notification
        from notifications.utils import create_notification
        create_notification(
            candidate_user,
            f'Payment Receipt — {invoice_number}',
            f'Your receipt for {payment.currency} {payment.amount:,.2f} is ready. '
            f'Check your email for the attached PDF.',
        )

    except Exception:
        pass  # Never let email failure break the API response
