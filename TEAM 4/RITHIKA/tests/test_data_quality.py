def validate_battery(value):
    return 0 <= value <= 100


def validate_speed(value):
    return value >= 0


def test_battery_range():
    assert validate_battery(50)


def test_battery_zero():
    assert validate_battery(0)


def test_speed_non_negative():
    assert validate_speed(80)