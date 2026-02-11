import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { useClaim } from "@/contexts/ClaimContext";
import { ArrowLeft, ArrowRight, Loader2 } from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";

type ClaimType = "health" | "vehicle" | "property" | "life";

const ClaimDetails = () => {
  const { state, submitClaimDetails } = useClaim();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!state.claimantType) {
      navigate("/claim/start", { replace: true });
    } else if (!state.claimType) {
      navigate("/claim/type", { replace: true });
    }
  }, [navigate, state.claimType, state.claimantType]);

  const initialData = useMemo(() => {
    const today = new Date().toISOString().slice(0, 10);
    switch (state.claimType) {
      case "health":
        return {
          patient_name: "",
          patient_age: 0,
          patient_relation: "",
          hospital_name: "",
          hospital_location: "",
          admission_date: today,
          discharge_date: today,
          diagnosis: "",
          treatment_type: "",
          treatment_description: "",
          total_bill_amount: 0,
          amount_claimed: 0,
          pre_existing_condition: false,
        } as const;
      case "vehicle":
        return {
          vehicle_type: "",
          vehicle_registration: "",
          vehicle_make: "",
          vehicle_model: "",
          vehicle_year: new Date().getFullYear(),
          accident_date: today,
          accident_location: "",
          accident_description: "",
          damage_type: "",
          estimated_repair_cost: 0,
          police_report_filed: false,
          third_party_involved: false,
        } as const;
      case "property":
        return {
          property_type: "",
          property_address: "",
          property_value: 0,
          ownership_type: "",
          incident_date: today,
          incident_type: "",
          incident_description: "",
          damage_description: "",
          estimated_loss: 0,
          amount_claimed: 0,
          police_report_filed: false,
          fire_brigade_report: false,
        } as const;
      case "life":
        return {
          policyholder_name: "",
          policyholder_dob: today,
          beneficiary_name: "",
          beneficiary_relation: "",
          claim_reason: "",
          event_date: today,
          event_description: "",
          cause_of_event: "",
          sum_assured: 0,
          amount_claimed: 0,
          death_certificate_available: false,
          medical_records_available: false,
        } as const;
      default:
        return {};
    }
  }, [state.claimType]);

  const [form, setForm] = useState<any>(initialData);

  useEffect(() => {
    setForm(initialData);
  }, [initialData]);

  if (!state.claimType || !state.claimantType) return null;

  const handleChange = (key: string, value: any) => {
    setForm((prev: any) => ({ ...prev, [key]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      await submitClaimDetails(
        { ...form, claim_id: state.claimId!, claimant_type: state.claimantType },
        state.claimType as ClaimType
      );
      navigate("/claim/id-verify");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to submit claim details");
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderFields = () => {
    const numberInput = (key: string, label: string) => (
      <div key={key} className="space-y-1.5">
        <Label htmlFor={key} className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </Label>
        <Input
          id={key}
          type="number"
          value={form[key] ?? ""}
          onChange={(e) => handleChange(key, Number(e.target.value))}
          className="h-11 bg-muted/30 border-border/60 focus:bg-white transition-colors"
        />
      </div>
    );

    const textInput = (key: string, label: string) => (
      <div key={key} className="space-y-1.5">
        <Label htmlFor={key} className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </Label>
        <Input
          id={key}
          value={form[key] ?? ""}
          onChange={(e) => handleChange(key, e.target.value)}
          className="h-11 bg-muted/30 border-border/60 focus:bg-white transition-colors"
        />
      </div>
    );

    const dateInput = (key: string, label: string) => (
      <div key={key} className="space-y-1.5">
        <Label htmlFor={key} className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </Label>
        <Input
          id={key}
          type="date"
          value={form[key] ?? ""}
          onChange={(e) => handleChange(key, e.target.value)}
          className="h-11 bg-muted/30 border-border/60 focus:bg-white transition-colors"
        />
      </div>
    );

    const textareaInput = (key: string, label: string) => (
      <div key={key} className="space-y-1.5 md:col-span-2">
        <Label htmlFor={key} className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          {label}
        </Label>
        <Textarea
          id={key}
          value={form[key] ?? ""}
          onChange={(e) => handleChange(key, e.target.value)}
          className="bg-muted/30 border-border/60 focus:bg-white transition-colors min-h-[80px]"
        />
      </div>
    );

    const checkboxInput = (key: string, label: string) => (
      <div key={key} className="flex items-center gap-3 py-2">
        <Checkbox
          id={key}
          checked={!!form[key]}
          onCheckedChange={(checked) => handleChange(key, Boolean(checked))}
          className="border-border"
        />
        <Label htmlFor={key} className="text-sm font-medium text-foreground cursor-pointer">
          {label}
        </Label>
      </div>
    );

    switch (state.claimType) {
      case "health":
        return [
          textInput("patient_name", "Patient name"),
          numberInput("patient_age", "Patient age"),
          textInput("patient_relation", "Relation to claimant"),
          textInput("hospital_name", "Hospital name"),
          textInput("hospital_location", "Hospital location"),
          dateInput("admission_date", "Admission date"),
          dateInput("discharge_date", "Discharge date"),
          textInput("diagnosis", "Diagnosis"),
          textInput("treatment_type", "Treatment type"),
          textareaInput("treatment_description", "Treatment description"),
          numberInput("total_bill_amount", "Total bill amount"),
          numberInput("amount_claimed", "Amount claimed"),
          checkboxInput("pre_existing_condition", "Pre-existing condition"),
        ];
      case "vehicle":
        return [
          textInput("vehicle_type", "Vehicle type"),
          textInput("vehicle_registration", "Registration number"),
          textInput("vehicle_make", "Make"),
          textInput("vehicle_model", "Model"),
          numberInput("vehicle_year", "Year"),
          dateInput("accident_date", "Accident date"),
          textInput("accident_location", "Accident location"),
          textareaInput("accident_description", "Accident description"),
          textInput("damage_type", "Damage type"),
          numberInput("estimated_repair_cost", "Estimated repair cost"),
          checkboxInput("police_report_filed", "Police report filed"),
          checkboxInput("third_party_involved", "Third party involved"),
        ];
      case "property":
        return [
          textInput("property_type", "Property type"),
          textInput("property_address", "Property address"),
          numberInput("property_value", "Property value"),
          textInput("ownership_type", "Ownership type"),
          dateInput("incident_date", "Incident date"),
          textInput("incident_type", "Incident type"),
          textareaInput("incident_description", "Incident description"),
          textareaInput("damage_description", "Damage description"),
          numberInput("estimated_loss", "Estimated loss"),
          numberInput("amount_claimed", "Amount claimed"),
          checkboxInput("police_report_filed", "Police report filed"),
          checkboxInput("fire_brigade_report", "Fire brigade report"),
        ];
      case "life":
        return [
          textInput("policyholder_name", "Policyholder name"),
          dateInput("policyholder_dob", "Policyholder DOB"),
          textInput("beneficiary_name", "Beneficiary name"),
          textInput("beneficiary_relation", "Beneficiary relation"),
          textInput("claim_reason", "Claim reason"),
          dateInput("event_date", "Event date"),
          textareaInput("event_description", "Event description"),
          textInput("cause_of_event", "Cause of event"),
          numberInput("sum_assured", "Sum assured"),
          numberInput("amount_claimed", "Amount claimed"),
          checkboxInput("death_certificate_available", "Death certificate available"),
          checkboxInput("medical_records_available", "Medical records available"),
        ];
      default:
        return [];
    }
  };

  const typeLabel = {
    health: "Health",
    vehicle: "Vehicle",
    property: "Property",
    life: "Life",
  }[state.claimType] || state.claimType;

  return (
    <ClaimLayout
      title={`${typeLabel} claim details`}
      subtitle="Complete all relevant fields below to proceed."
    >
      <Card className="shadow-premium border-0">
        <CardContent className="p-6 md:p-8">
          {error && (
            <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4 mb-6">
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}
          <form onSubmit={handleSubmit}>
            <div className="grid md:grid-cols-2 gap-x-5 gap-y-4">
              {renderFields()}
            </div>
            <div className="flex items-center justify-between pt-8 mt-6 border-t border-border/60">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate(-1)}
                disabled={isSubmitting}
                className="gap-2 text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              <Button
                type="submit"
                disabled={isSubmitting}
                className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
              >
                {isSubmitting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <>
                    Continue
                    <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </ClaimLayout>
  );
};

export default ClaimDetails;