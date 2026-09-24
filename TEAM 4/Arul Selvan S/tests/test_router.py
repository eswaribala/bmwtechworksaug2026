from bmw_analyst.agent.router import (
    AnalystIntent,
    IntentRouter,
)


router = IntentRouter()


def test_vehicle_sales_intent():
    assert (
        router.route(
            "Which BMW model sold the most vehicles?"
        )
        == AnalystIntent.VEHICLE_SALES
    )


def test_warranty_intent():
    assert (
        router.route(
            "Which model had the highest warranty cost?"
        )
        == AnalystIntent.WARRANTY_COST
    )


def test_fault_intent():
    assert (
        router.route(
            "What are the most common faults?"
        )
        == AnalystIntent.FAULT_SUMMARY
    )


def test_battery_intent():
    assert (
        router.route(
            "Which vehicles have low battery?"
        )
        == AnalystIntent.BATTERY_STATUS
    )


def test_custom_query():
    assert (
        router.route(
            "Compare average sales amount with warranty cost"
        )
        == AnalystIntent.CUSTOM_QUERY
    )


def test_empty_question():
    try:
        router.route("")
        assert False
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty."