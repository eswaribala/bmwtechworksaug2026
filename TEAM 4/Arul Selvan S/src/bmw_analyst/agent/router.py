from enum import Enum


class AnalystIntent(str, Enum):
    VEHICLE_SALES = "vehicle_sales"
    WARRANTY_COST = "warranty_cost"
    FAULT_SUMMARY = "fault_summary"
    BATTERY_STATUS = "battery_status"
    CUSTOM_QUERY = "custom_query"


class IntentRouter:

    VEHICLE_SALES_KEYWORDS = {
        "sale",
        "sales",
        "sold",
        "selling",
        "revenue",
        "quantity",
        "vehicle sales",
    }

    WARRANTY_KEYWORDS = {
        "warranty",
        "warranty cost",
        "warranty costs",
        "warranty claim",
        "warranty claims",
    }

    FAULT_KEYWORDS = {
        "fault",
        "faults",
        "failure",
        "failures",
        "fault type",
        "severity",
        "problem",
        "problems",
    }

    BATTERY_KEYWORDS = {
        "battery",
        "battery status",
        "battery percentage",
        "battery level",
        "charge",
        "charging",
        "low battery",
    }

    COMPARISON_KEYWORDS = {
        "compare",
        "comparison",
        "versus",
        "vs",
        "difference",
        "between",
    }

    def route(self, question: str) -> AnalystIntent:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        text = question.lower().strip()

        sales_match = self._contains_any(
            text,
            self.VEHICLE_SALES_KEYWORDS,
        )

        warranty_match = self._contains_any(
            text,
            self.WARRANTY_KEYWORDS,
        )

        fault_match = self._contains_any(
            text,
            self.FAULT_KEYWORDS,
        )

        battery_match = self._contains_any(
            text,
            self.BATTERY_KEYWORDS,
        )

        comparison_match = self._contains_any(
            text,
            self.COMPARISON_KEYWORDS,
        )

        matched_domains = sum(
            [
                sales_match,
                warranty_match,
                fault_match,
                battery_match,
            ]
        )

        # Multi-domain and comparison questions need the general SQL path so
        # the generator can preserve every requested part.
        if matched_domains > 1:
            return AnalystIntent.CUSTOM_QUERY

        if battery_match:
            return AnalystIntent.BATTERY_STATUS

        if warranty_match:
            return AnalystIntent.WARRANTY_COST

        if fault_match:
            return AnalystIntent.FAULT_SUMMARY

        if sales_match:
            return AnalystIntent.VEHICLE_SALES

        return AnalystIntent.CUSTOM_QUERY

    @staticmethod
    def _contains_any(
        text: str,
        keywords: set[str],
    ) -> bool:
        return any(
            keyword in text
            for keyword in keywords
        )