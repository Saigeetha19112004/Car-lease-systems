import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from ...db.session import engine
from ..models.models import ContractDocument
from sqlmodel import Session

STORAGE_DIR = os.getenv('CONTRACT_STORAGE_DIR', os.path.join(os.getcwd(), '..', '..', '..', 'storage', 'contracts'))
if not os.path.exists(STORAGE_DIR):
    os.makedirs(STORAGE_DIR, exist_ok=True)


def generate_contract_pdf(lease, template_values=None):
    """Generate a simple PDF contract for the lease and return the file path."""
    filename = f'contract_{lease.id}.pdf'
    path = os.path.join(STORAGE_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)

    text = c.beginText(40, 700)
    text.setFont('Helvetica', 12)
    text.textLine(f'Lease Contract: {lease.lease_number}')
    text.textLine('')
    text.textLine(f'Start Date: {lease.start_date}')
    text.textLine(f'End Date: {lease.end_date}')
    text.textLine(f'Monthly Payment: {lease.monthly_payment} USD')
    text.textLine(f'Total Amount: {lease.total_amount} USD')
    text.textLine('')
    text.textLine('Terms and Conditions:')
    text.textLine('1. This is a sample contract for demo purposes.')
    text.textLine('2. The lessee agrees to the mileage and return conditions.')
    c.drawText(text)

    c.showPage()
    c.save()

    # Save metadata to DB
    with Session(engine) as session:
        doc = ContractDocument(lease_id=lease.id, s3_url=path, status='generated')
        session.add(doc)
        session.commit()
        session.refresh(doc)
    return path, doc


def sign_contract(lease_id, signer_info: dict):
    with Session(engine) as session:
        doc = session.exec(select(ContractDocument).where(ContractDocument.lease_id == lease_id)).first()
        if not doc:
            return None
        doc.signer = signer_info
        doc.signed_at = datetime.utcnow()
        doc.status = 'signed'
        session.add(doc)
        session.commit()
        session.refresh(doc)
        return doc
