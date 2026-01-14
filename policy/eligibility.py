from datetime import date
from policy.plan_definitions import POLICY_PLANS

def evaluate_policy(
    plan_code: str,
    policy_expiry: date,
    event: str,
    amount_claimed: int
) -> tuple[bool, str]:
    today = date.today()

    if policy_expiry < today:
        return False, "Policy expired"

    plan = POLICY_PLANS.get(plan_code)
    if not plan:
        return False, "Unknown policy plan"

    event_def = plan["events_covered"].get(event)
    if not event_def or not event_def.get("covered"):
        return False, f"Event '{event}' not covered"

    max_amount = event_def.get("max_amount", 0)
    if amount_claimed > max_amount:
        return False, "Claim exceeds coverage limit"

    return True, "Policy eligible"
