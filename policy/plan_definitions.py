POLICY_PLANS = {
    "SILVER": {
        "plan_display_name": "Health Guard Silver",
        "sum_insured": {"currency": "INR", "max": 300_000},
        "events_covered": {
            "hospital_damages": {
                "covered": True,
                "max_amount": 300_000,
                "co_pay_percent": 0
            },
            "accident_injury": {
                "covered": True,
                "max_amount": 300_000,
                "waiting_period_years": 0
            },
            "property_damage": {
                "covered": False,
                "max_amount": 0,
                "waiting_period_years": 0
            }
        }
    },
    "GOLD": {
        "plan_display_name": "Health Guard Gold",
        "sum_insured": {"currency": "INR", "max": 5_000_000},
        "events_covered": {
            "hospital_damages": {
                "covered": True,
                "max_amount": 5_000_000,
                "co_pay_percent": 0
            },
            "accident_injury": {
                "covered": True,
                "max_amount": 5_000_000,
                "waiting_period_years": 0
            },
            "property_damage": {
                "covered": False,
                "max_amount": 0,
                "waiting_period_years": 0
            }
        }
    },
    "PLATINUM": {
        "plan_display_name": "Health Guard Platinum",
        "sum_insured": {"currency": "INR", "max": 10_000_000},
        "events_covered": {
            "hospital_damages": {
                "covered": True,
                "max_amount": 10_000_000,
                "co_pay_percent": 0
            },
            "accident_injury": {
                "covered": True,
                "max_amount": 10_000_000,
                "waiting_period_years": 0
            },
            "property_damage": {
                "covered": True,
                "max_amount": 10_000_000,
                "waiting_period_years": 0.5
            }
        }
    }
}
