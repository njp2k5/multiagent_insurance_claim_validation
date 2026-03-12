import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useClaim } from "@/contexts/ClaimContext";
import { ArrowLeft, ArrowRight, MessageSquare } from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";
import { terminalLog } from "@/lib/terminalLog";

const ClaimNarrative = () => {
  const { state, saveNarrative } = useClaim();
  const navigate = useNavigate();
  const [story, setStory] = useState(state.narrative || "");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    terminalLog("ClaimNarrative", "Mounted — claim_id:", state.claimId);
    if (!state.claimantType) navigate("/claim/start", { replace: true });
    else if (!state.claimType) navigate("/claim/type", { replace: true });
    else if (!state.details) navigate("/claim/details", { replace: true });
    else if (!state.aadhar) navigate("/claim/id-verify", { replace: true });
  }, [navigate, state.aadhar, state.claimType, state.claimantType, state.details]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    terminalLog("ClaimNarrative", "Saving narrative — claim_id:", state.claimId);
    if (!story.trim()) {
      setError("Please provide a brief account of what happened.");
      return;
    }
    saveNarrative(story.trim());
    navigate("/claim/documents");
  };

  const charCount = story.length;
  const minChars = 10;

  return (
    <ClaimLayout title="Tell us what happened" subtitle="Describe the incident in your own words.">
      <Card className="shadow-premium border-0">
        <CardContent className="p-6 md:p-8">
          {error && (
            <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4 mb-6">
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-3">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-accent/10 flex items-center justify-center">
                  <MessageSquare className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <Label htmlFor="narrative" className="text-base font-semibold text-foreground">
                    Incident Description
                  </Label>
                  <p className="text-xs text-muted-foreground">
                    A clear account helps us process your claim faster
                  </p>
                </div>
              </div>
              <Textarea
                id="narrative"
                minLength={minChars}
                rows={8}
                value={story}
                onChange={(e) => {
                  setStory(e.target.value);
                  if (error) setError(null);
                }}
                placeholder="Describe what happened, when it occurred, and any relevant circumstances..."
                className="bg-muted/30 border-border/60 focus:bg-white transition-colors text-sm leading-relaxed resize-none"
              />
              <div className="flex items-center justify-between">
                <p className={`text-xs font-medium ${charCount < minChars ? "text-muted-foreground" : "text-success"}`}>
                  {charCount} / {minChars} min characters
                </p>
                <div className="h-1 w-24 rounded-full bg-muted overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      charCount >= minChars ? "bg-success" : "bg-accent"
                    }`}
                    style={{ width: `${Math.min((charCount / minChars) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-border/60">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate(-1)}
                className="gap-2 text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              <Button
                type="submit"
                className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
              >
                Continue
                <ArrowRight className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </ClaimLayout>
  );
};

export default ClaimNarrative;