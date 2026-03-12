POLICY_PLANS = {
    "SILVER": {
        "plan_display_name": "Shield Silver",
        "sum_insured": {"currency": "INR", "max": 300_000},
        "events_covered": {
            "motor": {
                "covered": True,
                "max_amount": 150_000,
                "co_pay_percent": 10,
                "waiting_period_years": 0
            },
            "health": {
                "covered": True,
                "max_amount": 300_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "home": {
                "covered": False,
                "max_amount": 0,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "travel": {
                "covered": False,
                "max_amount": 0,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "life": {
                "covered": False,
                "max_amount": 0,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            }
        }
    },
    "GOLD": {
        "plan_display_name": "Shield Gold",
        "sum_insured": {"currency": "INR", "max": 5_000_000},
        "events_covered": {
            "motor": {
                "covered": True,
                "max_amount": 2_500_000,
                "co_pay_percent": 5,
                "waiting_period_years": 0
            },
            "health": {
                "covered": True,
                "max_amount": 5_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "home": {
                "covered": True,
                "max_amount": 2_000_000,
                "co_pay_percent": 5,
                "waiting_period_years": 0.5
            },
            "travel": {
                "covered": True,
                "max_amount": 500_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "life": {
                "covered": False,
                "max_amount": 0,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            }
        }
    },
    "PLATINUM": {
        "plan_display_name": "Shield Platinum",
        "sum_insured": {"currency": "INR", "max": 10_000_000},
        "events_covered": {
            "motor": {
                "covered": True,
                "max_amount": 5_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "health": {
                "covered": True,
                "max_amount": 10_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "home": {
                "covered": True,
                "max_amount": 5_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "travel": {
                "covered": True,
                "max_amount": 2_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 0
            },
            "life": {
                "covered": True,
                "max_amount": 10_000_000,
                "co_pay_percent": 0,
                "waiting_period_years": 1
            }
        }
    }
}
