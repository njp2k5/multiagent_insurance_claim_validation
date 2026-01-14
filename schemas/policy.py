from pydantic import BaseModel

class TestClaim(BaseModel):
    event: str
    amount_claimed: int

class PolicyCheckRequest(BaseModel):
    test_claim: TestClaim
    policy_plan_code: str
