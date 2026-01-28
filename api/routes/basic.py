from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum

from services.claim_store import claim_store

router = APIRouter(prefix="/claims", tags=["Claims - Event Categories"])


# ============== ENUMS ==============

class ClaimantType(str, Enum):
    user = "user"
    company = "company"


# ============== MOTOR CLAIM ==============

class MotorClaimRequest(BaseModel):
    claim_id: str
    claimant_type: ClaimantType
    vehicle_type: str = Field(..., description="Type of vehicle: car, bike, truck, etc.")
    vehicle_registration: str = Field(..., description="Vehicle registration number")
    vehicle_make: str = Field(..., description="Vehicle manufacturer")
    vehicle_model: str = Field(..., description="Vehicle model")
    vehicle_year: int = Field(..., description="Year of manufacture")
    accident_date: date = Field(..., description="Date of accident/incident")
    accident_location: str = Field(..., description="Location of accident")
    accident_description: str = Field(..., description="Brief description of the accident")
    damage_type: str = Field(..., description="Type of damage: collision, theft, fire, flood, etc.")
    estimated_repair_cost: float = Field(..., description="Estimated repair cost in INR")
    police_report_filed: bool = Field(default=False, description="Whether police report was filed")
    third_party_involved: bool = Field(default=False, description="Whether third party was involved")


@router.post("/motor")
def submit_motor_claim(request: MotorClaimRequest):
    """
    Submit a motor insurance claim with vehicle and accident details.
    Updates the claim state with motor-specific information.
    """
    state = claim_store.get_claim(request.claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {request.claim_id} not found")
    
    # Update state with motor claim info
    state["claimant_type"] = request.claimant_type.value
    state["claim_type"] = "motor"
    
    motor_details = {
        "vehicle_type": request.vehicle_type,
        "vehicle_registration": request.vehicle_registration,
        "vehicle_make": request.vehicle_make,
        "vehicle_model": request.vehicle_model,
        "vehicle_year": request.vehicle_year,
        "accident_date": request.accident_date.isoformat(),
        "accident_location": request.accident_location,
        "accident_description": request.accident_description,
        "damage_type": request.damage_type,
        "estimated_repair_cost": request.estimated_repair_cost,
        "police_report_filed": request.police_report_filed,
        "third_party_involved": request.third_party_involved
    }
    
    state["motor_details"] = motor_details
    state["claim_form"] = {
        "claimant_type": request.claimant_type.value,
        "claim_type": "motor",
        "event": "motor",
        "amount_claimed": request.estimated_repair_cost,
        **motor_details
    }
    
    claim_store.update_claim(request.claim_id, state)
    
    return {
        "claim_id": request.claim_id,
        "claim_type": "motor",
        "status": "submitted",
        "message": "Motor claim details saved successfully",
        "details": motor_details
    }


# ============== HEALTH CLAIM ==============

class HealthClaimRequest(BaseModel):
    claim_id: str
    claimant_type: ClaimantType
    patient_name: str = Field(..., description="Name of the patient")
    patient_age: int = Field(..., description="Age of the patient")
    patient_relation: str = Field(..., description="Relation to policyholder: self, spouse, child, parent")
    hospital_name: str = Field(..., description="Name of the hospital")
    hospital_location: str = Field(..., description="Hospital city/location")
    admission_date: date = Field(..., description="Date of hospital admission")
    discharge_date: Optional[date] = Field(None, description="Date of discharge (if discharged)")
    diagnosis: str = Field(..., description="Medical diagnosis")
    treatment_type: str = Field(..., description="Type of treatment: surgery, medication, therapy, etc.")
    treatment_description: str = Field(..., description="Description of treatment received")
    total_bill_amount: float = Field(..., description="Total hospital bill amount in INR")
    amount_claimed: float = Field(..., description="Amount being claimed in INR")
    pre_existing_condition: bool = Field(default=False, description="Whether it's a pre-existing condition")


@router.post("/health")
def submit_health_claim(request: HealthClaimRequest):
    """
    Submit a health insurance claim with patient and treatment details.
    Updates the claim state with health-specific information.
    """
    state = claim_store.get_claim(request.claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {request.claim_id} not found")
    
    # Update state with health claim info
    state["claimant_type"] = request.claimant_type.value
    state["claim_type"] = "health"
    
    health_details = {
        "patient_name": request.patient_name,
        "patient_age": request.patient_age,
        "patient_relation": request.patient_relation,
        "hospital_name": request.hospital_name,
        "hospital_location": request.hospital_location,
        "admission_date": request.admission_date.isoformat(),
        "discharge_date": request.discharge_date.isoformat() if request.discharge_date else None,
        "diagnosis": request.diagnosis,
        "treatment_type": request.treatment_type,
        "treatment_description": request.treatment_description,
        "total_bill_amount": request.total_bill_amount,
        "amount_claimed": request.amount_claimed,
        "pre_existing_condition": request.pre_existing_condition
    }
    
    state["health_details"] = health_details
    state["claim_form"] = {
        "claimant_type": request.claimant_type.value,
        "claim_type": "health",
        "event": "health",
        "amount_claimed": request.amount_claimed,
        "claimant_name": request.patient_name,
        "age": request.patient_age,
        **health_details
    }
    
    claim_store.update_claim(request.claim_id, state)
    
    return {
        "claim_id": request.claim_id,
        "claim_type": "health",
        "status": "submitted",
        "message": "Health claim details saved successfully",
        "details": health_details
    }


# ============== HOME CLAIM ==============

class HomeClaimRequest(BaseModel):
    claim_id: str
    claimant_type: ClaimantType
    property_type: str = Field(..., description="Type of property: apartment, house, villa, etc.")
    property_address: str = Field(..., description="Full address of the property")
    property_value: float = Field(..., description="Estimated property value in INR")
    ownership_type: str = Field(..., description="Ownership type: owned, rented, leased")
    incident_date: date = Field(..., description="Date of incident")
    incident_type: str = Field(..., description="Type of incident: fire, flood, theft, earthquake, etc.")
    incident_description: str = Field(..., description="Description of the incident")
    damage_description: str = Field(..., description="Description of damage to property")
    estimated_loss: float = Field(..., description="Estimated loss amount in INR")
    amount_claimed: float = Field(..., description="Amount being claimed in INR")
    police_report_filed: bool = Field(default=False, description="Whether police report was filed")
    fire_brigade_report: bool = Field(default=False, description="Whether fire brigade report exists")


@router.post("/home")
def submit_home_claim(request: HomeClaimRequest):
    """
    Submit a home insurance claim with property and damage details.
    Updates the claim state with home-specific information.
    """
    state = claim_store.get_claim(request.claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {request.claim_id} not found")
    
    # Update state with home claim info
    state["claimant_type"] = request.claimant_type.value
    state["claim_type"] = "home"
    
    home_details = {
        "property_type": request.property_type,
        "property_address": request.property_address,
        "property_value": request.property_value,
        "ownership_type": request.ownership_type,
        "incident_date": request.incident_date.isoformat(),
        "incident_type": request.incident_type,
        "incident_description": request.incident_description,
        "damage_description": request.damage_description,
        "estimated_loss": request.estimated_loss,
        "amount_claimed": request.amount_claimed,
        "police_report_filed": request.police_report_filed,
        "fire_brigade_report": request.fire_brigade_report
    }
    
    state["home_details"] = home_details
    state["claim_form"] = {
        "claimant_type": request.claimant_type.value,
        "claim_type": "home",
        "event": "home",
        "amount_claimed": request.amount_claimed,
        **home_details
    }
    
    claim_store.update_claim(request.claim_id, state)
    
    return {
        "claim_id": request.claim_id,
        "claim_type": "home",
        "status": "submitted",
        "message": "Home claim details saved successfully",
        "details": home_details
    }


# ============== TRAVEL CLAIM ==============

class TravelClaimRequest(BaseModel):
    claim_id: str
    claimant_type: ClaimantType
    trip_type: str = Field(..., description="Type of trip: domestic, international")
    destination: str = Field(..., description="Travel destination")
    departure_date: date = Field(..., description="Departure date")
    return_date: date = Field(..., description="Return date")
    incident_date: date = Field(..., description="Date of incident")
    incident_type: str = Field(..., description="Type of incident: trip_cancellation, medical_emergency, baggage_loss, flight_delay, etc.")
    incident_location: str = Field(..., description="Location where incident occurred")
    incident_description: str = Field(..., description="Description of the incident")
    amount_claimed: float = Field(..., description="Amount being claimed in INR")
    booking_reference: Optional[str] = Field(None, description="Booking/ticket reference number")
    airline_name: Optional[str] = Field(None, description="Airline name if applicable")
    hotel_name: Optional[str] = Field(None, description="Hotel name if applicable")


@router.post("/travel")
def submit_travel_claim(request: TravelClaimRequest):
    """
    Submit a travel insurance claim with trip and incident details.
    Updates the claim state with travel-specific information.
    """
    state = claim_store.get_claim(request.claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {request.claim_id} not found")
    
    # Update state with travel claim info
    state["claimant_type"] = request.claimant_type.value
    state["claim_type"] = "travel"
    
    travel_details = {
        "trip_type": request.trip_type,
        "destination": request.destination,
        "departure_date": request.departure_date.isoformat(),
        "return_date": request.return_date.isoformat(),
        "incident_date": request.incident_date.isoformat(),
        "incident_type": request.incident_type,
        "incident_location": request.incident_location,
        "incident_description": request.incident_description,
        "amount_claimed": request.amount_claimed,
        "booking_reference": request.booking_reference,
        "airline_name": request.airline_name,
        "hotel_name": request.hotel_name
    }
    
    state["travel_details"] = travel_details
    state["claim_form"] = {
        "claimant_type": request.claimant_type.value,
        "claim_type": "travel",
        "event": "travel",
        "amount_claimed": request.amount_claimed,
        **travel_details
    }
    
    claim_store.update_claim(request.claim_id, state)
    
    return {
        "claim_id": request.claim_id,
        "claim_type": "travel",
        "status": "submitted",
        "message": "Travel claim details saved successfully",
        "details": travel_details
    }


# ============== LIFE CLAIM ==============

class LifeClaimRequest(BaseModel):
    claim_id: str
    claimant_type: ClaimantType
    policyholder_name: str = Field(..., description="Name of the policyholder")
    policyholder_dob: date = Field(..., description="Date of birth of policyholder")
    beneficiary_name: str = Field(..., description="Name of the beneficiary/claimant")
    beneficiary_relation: str = Field(..., description="Relation to policyholder: spouse, child, parent, nominee")
    claim_reason: str = Field(..., description="Reason for claim: death, critical_illness, disability, maturity")
    event_date: date = Field(..., description="Date of event (death/diagnosis/disability)")
    event_description: str = Field(..., description="Description of the event")
    cause_of_event: str = Field(..., description="Cause: natural, accidental, illness")
    sum_assured: float = Field(..., description="Sum assured in the policy in INR")
    amount_claimed: float = Field(..., description="Amount being claimed in INR")
    death_certificate_available: bool = Field(default=False, description="Whether death certificate is available")
    medical_records_available: bool = Field(default=False, description="Whether medical records are available")


@router.post("/life")
def submit_life_claim(request: LifeClaimRequest):
    """
    Submit a life insurance claim with policyholder and event details.
    Updates the claim state with life-specific information.
    """
    state = claim_store.get_claim(request.claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {request.claim_id} not found")
    
    # Update state with life claim info
    state["claimant_type"] = request.claimant_type.value
    state["claim_type"] = "life"
    
    life_details = {
        "policyholder_name": request.policyholder_name,
        "policyholder_dob": request.policyholder_dob.isoformat(),
        "beneficiary_name": request.beneficiary_name,
        "beneficiary_relation": request.beneficiary_relation,
        "claim_reason": request.claim_reason,
        "event_date": request.event_date.isoformat(),
        "event_description": request.event_description,
        "cause_of_event": request.cause_of_event,
        "sum_assured": request.sum_assured,
        "amount_claimed": request.amount_claimed,
        "death_certificate_available": request.death_certificate_available,
        "medical_records_available": request.medical_records_available
    }
    
    state["life_details"] = life_details
    state["claim_form"] = {
        "claimant_type": request.claimant_type.value,
        "claim_type": "life",
        "event": "life",
        "amount_claimed": request.amount_claimed,
        "claimant_name": request.beneficiary_name,
        **life_details
    }
    
    claim_store.update_claim(request.claim_id, state)
    
    return {
        "claim_id": request.claim_id,
        "claim_type": "life",
        "status": "submitted",
        "message": "Life claim details saved successfully",
        "details": life_details
    }


# ============== GET CLAIM DETAILS ==============

@router.get("/{claim_id}")
def get_claim_details(claim_id: str):
    """
    Get the current state and details of a claim.
    """
    state = claim_store.get_claim(claim_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Claim {claim_id} not found")
    
    claim_type = state.get("claim_type")
    
    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "claimant_type": state.get("claimant_type"),
        "claim_form": state.get("claim_form"),
        "motor_details": state.get("motor_details"),
        "health_details": state.get("health_details"),
        "home_details": state.get("home_details"),
        "travel_details": state.get("travel_details"),
        "life_details": state.get("life_details"),
        "document_summary": state.get("document_summary"),
        "identity_result": state.get("identity_result"),
        "policy_result": state.get("policy_result"),
        "fraud_result": state.get("fraud_result"),
        "final_decision": state.get("final_decision"),
        "final_confidence": state.get("final_confidence")
    }
