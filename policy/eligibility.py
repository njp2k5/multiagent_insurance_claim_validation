from datetime import date
from typing import Dict, Any, Tuple
from policy.plan_definitions import POLICY_PLANS


def get_coverage_details(plan_code: str, event: str) -> Dict[str, Any]:
    """
    Get detailed coverage information for a specific event under a plan.
    Returns coverage details including max_amount, co_pay_percent, waiting_period.
    """
    plan = POLICY_PLANS.get(plan_code)
    if not plan:
        return {"covered": False, "reason": "Unknown policy plan"}
    
    event_def = plan["events_covered"].get(event)
    if not event_def:
        return {"covered": False, "reason": f"Event '{event}' not defined in plan"}
    
    return {
        "covered": event_def.get("covered", False),
        "max_amount": event_def.get("max_amount", 0),
        "co_pay_percent": event_def.get("co_pay_percent", 0),
        "waiting_period_years": event_def.get("waiting_period_years", 0),
        "plan_name": plan.get("plan_display_name"),
        "sum_insured": plan.get("sum_insured", {})
    }


def evaluate_policy(
    plan_code: str,
    policy_expiry: date,
    event: str,
    amount_claimed: float,
    policy_start_date: date = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Evaluate whether a claim is covered under the policy.
    
    Args:
        plan_code: The policy plan code (SILVER, GOLD, PLATINUM)
        policy_expiry: Policy expiry date
        event: Event type (motor, health, home, travel, life)
        amount_claimed: Amount being claimed
        policy_start_date: Policy start date (for waiting period check)
    
    Returns:
        Tuple of (eligible: bool, message: str, details: dict)
    """
    today = date.today()
    details: Dict[str, Any] = {
        "plan_code": plan_code,
        "event": event,
        "amount_claimed": amount_claimed
    }

    # Check policy expiry
    if policy_expiry < today:
        details["reason"] = "policy_expired"
        details["policy_expiry"] = policy_expiry.isoformat()
        return False, "Policy has expired", details

    # Get plan details
    plan = POLICY_PLANS.get(plan_code)
    if not plan:
        details["reason"] = "unknown_plan"
        return False, f"Unknown policy plan: {plan_code}", details

    details["plan_name"] = plan.get("plan_display_name")
    details["sum_insured"] = plan.get("sum_insured", {})

    # Get event coverage
    event_def = plan["events_covered"].get(event)
    if not event_def:
        details["reason"] = "event_not_defined"
        details["available_events"] = list(plan["events_covered"].keys())
        return False, f"Event '{event}' is not defined in your plan", details

    if not event_def.get("covered", False):
        details["reason"] = "event_not_covered"
        details["covered"] = False
        return False, f"Event '{event}' is not covered under your {plan.get('plan_display_name')} plan", details

    # Add coverage details
    max_amount = event_def.get("max_amount", 0)
    co_pay_percent = event_def.get("co_pay_percent", 0)
    waiting_period_years = event_def.get("waiting_period_years", 0)
    
    details["covered"] = True
    details["max_amount"] = max_amount
    details["co_pay_percent"] = co_pay_percent
    details["waiting_period_years"] = waiting_period_years

    # Check waiting period
    if waiting_period_years > 0 and policy_start_date:
        waiting_end_date = date(
            policy_start_date.year + int(waiting_period_years),
            policy_start_date.month,
            policy_start_date.day
        )
        if today < waiting_end_date:
            details["reason"] = "waiting_period"
            details["waiting_end_date"] = waiting_end_date.isoformat()
            return False, f"Claim is within waiting period. Coverage starts from {waiting_end_date}", details

    # Check claim amount against coverage limit
    if amount_claimed > max_amount:
        details["reason"] = "exceeds_limit"
        details["excess_amount"] = amount_claimed - max_amount
        return False, f"Claim amount (₹{amount_claimed:,.0f}) exceeds coverage limit (₹{max_amount:,.0f})", details

    # Calculate co-pay if applicable
    if co_pay_percent > 0:
        co_pay_amount = amount_claimed * (co_pay_percent / 100)
        claimable_amount = amount_claimed - co_pay_amount
        details["co_pay_amount"] = co_pay_amount
        details["claimable_amount"] = claimable_amount
        return True, f"Claim eligible. You pay ₹{co_pay_amount:,.0f} ({co_pay_percent}% co-pay). Claimable: ₹{claimable_amount:,.0f}", details

    details["claimable_amount"] = amount_claimed
    return True, f"Claim eligible for full amount of ₹{amount_claimed:,.0f}", details
