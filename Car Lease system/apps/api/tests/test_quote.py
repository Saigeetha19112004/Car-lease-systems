from app.services.quote import calculate_quote

def test_calculate_quote_basic():
    monthly, breakdown, expires = calculate_quote(30000, 36, down_payment=1500)
    assert monthly > 0
    assert 'base' in breakdown
    assert 'taxes' in breakdown
