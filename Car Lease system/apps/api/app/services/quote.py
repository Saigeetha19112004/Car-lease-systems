from datetime import datetime, timedelta

# Simple quote calculator for MVP
# monthly_payment = (base_price - residual/term) + taxes + fees - down_payment/term

def calculate_quote(base_price: float, term_months: int, down_payment: float = 0.0, tax_rate: float = 0.08, fees: float = 0.0, residual: float = None):
    if residual is None:
        # naive residual estimate: 55% at 36 months, roughly linear
        base_residual_pct = {24: 0.65, 36: 0.55, 48: 0.45}
        residual_pct = base_residual_pct.get(term_months, 0.5)
        residual = base_price * residual_pct

    monthly_depreciation = (base_price - residual) / term_months
    base_monthly = monthly_depreciation

    monthly_down = down_payment / term_months if term_months else 0
    taxes = (base_monthly + fees) * tax_rate

    monthly_payment = base_monthly + fees + taxes - monthly_down

    # Expiry in 7 days
    expires_at = datetime.utcnow() + timedelta(days=7)

    breakdown = {
        'base': round(base_monthly,2),
        'fees': round(fees,2),
        'taxes': round(taxes,2),
        'residual': round(residual,2)
    }

    return round(monthly_payment,2), breakdown, expires_at
