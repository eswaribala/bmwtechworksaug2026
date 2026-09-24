from src.recommendation.recommendation_engine import recommend_inventory


# Test 1: Valid dealer and model
def test_valid_recommendation():
    result = recommend_inventory("D001", "i4")

    assert result["Dealer"] == "D001"
    assert result["Model"] == "i4"
    assert result["Recommended Quantity"] >= 0


# Test 2: Invalid dealer
def test_invalid_dealer():
    try:
        recommend_inventory("D999", "i4")
        assert False
    except ValueError:
        assert True


# Test 3: Invalid model
def test_invalid_model():
    try:
        recommend_inventory("D001", "InvalidModel")
        assert False
    except ValueError:
        assert True


# Test 4: Recommended quantity should never be negative
def test_recommended_quantity_not_negative():
    result = recommend_inventory("D001", "i4")

    assert result["Recommended Quantity"] >= 0


# Test 5: Required output fields should exist
def test_required_output_fields():
    result = recommend_inventory("D001", "i4")

    required_fields = [
        "Dealer",
        "Model",
        "Recommended Quantity",
        "Predicted Next Month Demand",
        "Current Inventory",
        "Target Inventory",
        "Days of Inventory",
        "Sales Trend",
        "Reason",
    ]

    for field in required_fields:
        assert field in result