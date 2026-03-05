import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { useClaim } from "@/contexts/ClaimContext";
import { User, Building2, Loader2 } from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";
import { terminalLog } from "@/lib/terminalLog";

const ClaimStart = () => {
  const { startNewClaim, setClaimantType } = useClaim();
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const hasInitialized = useRef(false);

  useEffect(() => {
    // Ensure we only run once per component lifetime
    if (hasInitialized.current) {
      terminalLog("ClaimStart", "Already initialized, skipping");
      return;
    }
    hasInitialized.current = true;
    terminalLog("ClaimStart", "Initializing claim...");

    const init = async () => {
      setIsCreating(true);
      setError(null);
      try {
        const claimId = await startNewClaim();
        terminalLog("ClaimStart", "Initialized with claim_id:", claimId);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to start claim");
      } finally {
        setIsCreating(false);
      }
    };
    void init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelect = (type: "user" | "company") => {
    setClaimantType(type);
    navigate("/claim/type");
  };

  const options = [
    {
      type: "user" as const,
      icon: User,
      label: "Individual",
      desc: "Submit a claim as a person",
      gradient: "from-blue-500 to-blue-600",
      bg: "bg-blue-50",
      color: "text-blue-600",
    },
    {
      type: "company" as const,
      icon: Building2,
      label: "Company",
      desc: "Submit on behalf of a business",
      gradient: "from-violet-500 to-purple-600",
      bg: "bg-violet-50",
      color: "text-violet-600",
    },
  ];

  return (
    <ClaimLayout title="Who is filing the claim?" subtitle="Select the type of claimant to get started.">
      {isCreating && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Initializing your claim...</span>
        </div>
      )}
      {error && (
        <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4 mb-4">
          <p className="text-sm text-destructive font-medium">{error}</p>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-5">
        {options.map((opt) => (
          <Card
            key={opt.type}
            onClick={() => !isCreating && handleSelect(opt.type)}
            className={`group cursor-pointer border-border/60 shadow-premium hover:shadow-card-hover hover:border-accent/30 transition-all duration-500 overflow-hidden ${
              isCreating ? "opacity-60 pointer-events-none" : ""
            }`}
          >
            <CardContent className="p-8 flex flex-col items-center text-center gap-4">
              <div
                className={`w-16 h-16 rounded-2xl ${opt.bg} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}
              >
                <opt.icon className={`h-8 w-8 ${opt.color}`} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground font-sans mb-1">{opt.label}</h3>
                <p className="text-sm text-muted-foreground">{opt.desc}</p>
              </div>
              <div className="w-full h-1 rounded-full bg-muted overflow-hidden mt-2">
                <div className={`h-full w-0 group-hover:w-full bg-gradient-to-r ${opt.gradient} transition-all duration-700 rounded-full`} />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </ClaimLayout>
  );
};

export default ClaimStart;