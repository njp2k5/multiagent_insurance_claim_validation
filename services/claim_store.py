"""
In-memory claim state store for managing claim states across agent invocations.
In production, this should be replaced with a database-backed store.
"""
from typing import Dict, Optional
from state import ClaimState
import uuid


class ClaimStore:
    """Singleton store for managing claim states."""
    _instance: Optional["ClaimStore"] = None
    _states: Dict[str, ClaimState]
    
    def __new__(cls) -> "ClaimStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._states = {}
        return cls._instance
    
    def create_claim(self, initial_state: Optional[ClaimState] = None) -> str:
        """Create a new claim and return its ID."""
        claim_id = str(uuid.uuid4())
        state: ClaimState = initial_state.copy() if initial_state else {}
        state["claim_id"] = claim_id
        state["cross_agent_data"] = state.get("cross_agent_data", {})
        state["agent_results"] = state.get("agent_results", [])
        self._states[claim_id] = state
        return claim_id
    
    def get_claim(self, claim_id: str) -> Optional[ClaimState]:
        """Get claim state by ID."""
        return self._states.get(claim_id)
    
    def update_claim(self, claim_id: str, state: ClaimState) -> None:
        """Update claim state."""
        if claim_id in self._states:
            self._states[claim_id] = state
    
    def delete_claim(self, claim_id: str) -> bool:
        """Delete claim state."""
        if claim_id in self._states:
            del self._states[claim_id]
            return True
        return False
    
    def list_claims(self) -> Dict[str, ClaimState]:
        """List all claims."""
        return self._states.copy()


# Global instance
claim_store = ClaimStore()
