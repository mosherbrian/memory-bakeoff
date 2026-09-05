from ledger.money import charge

def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('2.675') == '2.68'

def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('-2.675') == '-2.68'
from ledger.money import charge

def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('2.675') == '2.68'

def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('-2.675') == '-2.68'

def test_half_away_from_zero_positive_edge():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('0.005') == '0.01'

def test_half_away_from_zero_negative_edge():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('-0.005') == '-0.01'

def test_returns_string_with_exactly_two_decimals_zero_fraction():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('2.0')
    assert result == '2.00'

def test_halfway_negative_towards_larger_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge('-1.005') == '-1.01'
from ledger.money import charge

def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge('2.675') == '2.68'

def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge('-2.675') == '-2.68'

def test_exact_two_decimals_zero():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('0')
    assert result == '0.00'