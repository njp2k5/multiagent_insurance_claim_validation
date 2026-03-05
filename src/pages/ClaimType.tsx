import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { useClaim } from "@/contexts/ClaimContext";
import { Heart, Car, Home, Users, Loader2 } from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";
import { terminalLog } from "@/lib/terminalLog";

const claimTypes = [
  {
    key: "health" as const,
    label: "Health Insurance",
    desc: "Medical expenses, hospitalization",
    icon: Heart,
    bg: "bg-rose-50",
    color: "text-rose-600",
    gradient: "from-rose-500 to-pink-500",
  },
  {
    key: "vehicle" as const,
    label: "Vehicle Insurance",
    desc: "Accidents, damage, theft",
    icon: Car,
    bg: "bg-blue-50",
    color: "text-blue-600",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    key: "property" as const,
    label: "Property Insurance",
    desc: "Home, fire, natural disasters",
    icon: Home,
    bg: "bg-amber-50",
    color: "text-amber-600",
    gradient: "from-amber-500 to-orange-500",
  },
  {
    key: "life" as const,
    label: "Life Insurance",
    desc: "Life cover, term insurance",
    icon: Users,
    bg: "bg-emerald-50",
    color: "text-emerald-600",
    gradient: "from-emerald-500 to-green-500",
  },
];

const ClaimType = () => {
  const { state, ensureClaimId, submitClaimType } = useClaim();
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    terminalLog("ClaimType", "Mounted — claim_id:", state.claimId);
    if (!state.claimantType) {
      navigate("/claim/start", { replace: true });
      return;
    }
    void ensureClaimId();
  }, [ensureClaimId, navigate, state.claimantType]);

  const handleSelect = async (type: "health" | "vehicle" | "property" | "life") => {
    terminalLog("ClaimType", "Selected:", type, "— claim_id:", state.claimId);
    setIsSubmitting(true);
    setError(null);
    try {
      await submitClaimType(type);
      navigate("/claim/details");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save claim info");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ClaimLayout title="Select insurance type" subtitle="Choose the category that best matches your claim.">
      {error && (
        <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4 mb-4">
          <p className="text-sm text-destructive font-medium">{error}</p>
        </div>
      )}

      {isSubmitting && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Saving...</span>
        </div>
      )}

      <div className="grid sm:grid-cols-2 gap-4">
        {claimTypes.map((item) => (
          <Card
            key={item.key}
            onClick={() => !isSubmitting && handleSelect(item.key)}
            className={`group cursor-pointer border-border/60 shadow-premium hover:shadow-card-hover hover:border-accent/20 transition-all duration-500 overflow-hidden ${
              isSubmitting ? "opacity-60 pointer-events-none" : ""
            }`}
          >
            <CardContent className="p-6 flex items-start gap-4">
              <div
                className={`w-12 h-12 rounded-xl ${item.bg} flex items-center justify-center shrink-0 group-hover:scale-110 transition-transform duration-300`}
              >
                <item.icon className={`h-6 w-6 ${item.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-base font-semibold text-foreground font-sans mb-0.5">
                  {item.label}
                </h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
                <div className="w-full h-0.5 rounded-full bg-muted overflow-hidden mt-3">
                  <div
                    className={`h-full w-0 group-hover:w-full bg-gradient-to-r ${item.gradient} transition-all duration-700 rounded-full`}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </ClaimLayout>
  );
};

export default ClaimType;