from ledger.money import charge

def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('2.675') == '2.68'

def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('-2.675') == '-2.68'

def test_half_away_from_zero_negative_smaller_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('-2.665') == '-2.67'

def test_half_away_from_zero_positive_smaller_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68", and "-2.675" becomes "-2.68"."""
    assert charge('2.665') == '2.67'

def test_returns_string_with_exactly_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    assert charge('10') == '10.00'
    assert charge('10.1') == '10.10'
    assert charge('10.123') == '10.12'

def test_no_float_precision_errors_for_halfway_values():
    """REQUIREMENT: Amounts are given as strings precisely so that a halfway value means what it says. Converting through a binary float loses that, because a value such as 2.675 is not stored exactly and can round the wrong way."""
    assert charge('2.675') == '2.68'
    assert charge('2.685') == '2.69'
    assert charge('2.695') == '2.70'
    assert charge('2.705') == '2.71'
    assert charge('2.715') == '2.72'
    assert charge('2.725') == '2.73'
    assert charge('2.735') == '2.74'
    assert charge('2.745') == '2.75'
    assert charge('2.755') == '2.76'
    assert charge('2.765') == '2.77'
    assert charge('2.775') == '2.78'
    assert charge('2.785') == '2.79'
    assert charge('2.795') == '2.80'
    assert charge('2.805') == '2.81'
    assert charge('2.815') == '2.82'
    assert charge('2.825') == '2.83'
    assert charge('2.835') == '2.84'
    assert charge('2.845') == '2.85'
    assert charge('2.855') == '2.86'
    assert charge('2.865') == '2.87'
    assert charge('2.875') == '2.88'
    assert charge('2.885') == '2.89'
    assert charge('2.895') == '2.90'
    assert charge('2.905') == '2.91'
    assert charge('2.915') == '2.92'
    assert charge('2.925') == '2.93'
    assert charge('2.935') == '2.94'
    assert charge('2.945') == '2.95'
    assert charge('2.955') == '2.96'
    assert charge('2.965') == '2.97'
    assert charge('2.975') == '2.98'
    assert charge('2.985') == '2.99'
    assert charge('2.995') == '3.00'
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

def test_returns_string_with_exactly_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('2.341')
    assert isinstance(result, str)
    assert len(result.split('.')[1]) == 2

def test_returns_string_with_exactly_two_decimals_zero_fraction():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('2.0')
    assert result == '2.00'

def test_returns_string_with_exactly_two_decimals_negative_zero_fraction():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('-2.0')
    assert result == '-2.00'

def test_halfway_positive_towards_larger_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge('1.005') == '1.01'

def test_halfway_negative_towards_larger_magnitude():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge('-1.005') == '-1.01'

def test_halfway_larger_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge('9.995') == '10.00'

def test_halfway_larger_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude."""
    assert charge('-9.995') == '-10.00'

def test_no_float_conversion_accuracy_issue():
    """REQUIREMENT: Amounts are given as strings precisely so that a halfway value means what it says. Converting through a binary float loses that, because a value such as 2.675 is not stored exactly and can round the wrong way."""
    assert charge('2.675') == '2.68'
    assert charge('1.335') == '1.34'
    assert charge('1.345') == '1.35'
from ledger.money import charge

def test_half_away_from_zero_positive():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge('2.675') == '2.68'

def test_half_away_from_zero_negative():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge('-2.675') == '-2.68'

def test_half_away_from_zero_positive_other():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "2.675" becomes "2.68" """
    assert charge('1.005') == '1.01'

def test_half_away_from_zero_negative_other():
    """REQUIREMENT: Rounding is half away from zero: an amount exactly halfway between two hundredths goes to the larger magnitude. "-2.675" becomes "-2.68" """
    assert charge('-1.005') == '-1.01'

def test_exact_two_decimals():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('2.341')
    assert '.' in result
    assert len(result.split('.')[1]) == 2

def test_exact_two_decimals_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('-2.675')
    assert '.' in result
    assert len(result.split('.')[1]) == 2

def test_exact_two_decimals_zero():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('0')
    assert result == '0.00'

def test_exact_two_decimals_zero_negative():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('-0')
    assert result == '0.00'

def test_exact_two_decimals_zero_negative_sign():
    """REQUIREMENT: charge(amount) takes a money amount as a decimal string and returns it rounded to two decimal places, also as a string with exactly two decimals."""
    result = charge('-0.0')
    assert result == '0.00'

def test_no_float_conversion_error_for_halfway():
    """REQUIREMENT: Amounts are given as strings precisely so that a halfway value means what it says. Converting through a binary float loses that, because a value such as 2.675 is not stored exactly and can round the wrong way."""
    assert charge('2.675') == '2.68'
    assert charge('1.005') == '1.01'
    assert charge('1.015') == '1.02'
    assert charge('1.025') == '1.03'
    assert charge('1.035') == '1.04'
    assert charge('1.045') == '1.05'
    assert charge('1.055') == '1.06'
    assert charge('1.065') == '1.07'
    assert charge('1.075') == '1.08'
    assert charge('1.085') == '1.09'
    assert charge('1.095') == '1.10'