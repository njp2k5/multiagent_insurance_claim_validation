import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useClaim } from "@/contexts/ClaimContext";
import {
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  LayoutDashboard,
  ShieldCheck,
  Mail,
  TrendingUp,
  Award,
  Send,
} from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";

type StepState = "idle" | "working" | "done" | "error";

const AnimatedCircle = ({ state, delay = 0 }: { state: StepState; delay?: number }) => {
  const size = 80;
  const stroke = 4;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  const getProgress = () => {
    switch (state) {
      case "idle": return 0;
      case "working": return 0.7;
      case "done": return 1;
      case "error": return 1;
      default: return 0;
    }
  };

  const getColor = () => {
    switch (state) {
      case "working": return "url(#processing-gradient)";
      case "done": return "hsl(152 69% 42%)";
      case "error": return "hsl(0 84% 60%)";
      default: return "hsl(var(--muted))";
    }
  };

  const offset = circumference * (1 - getProgress());

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
        <defs>
          <linearGradient id="processing-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="hsl(217 91% 30%)" />
            <stop offset="100%" stopColor="hsl(199 89% 48%)" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={stroke}
          opacity={0.3}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{
            transition: "stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)",
            transitionDelay: `${delay}ms`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        {state === "working" && <Loader2 className="h-6 w-6 animate-spin text-accent" />}
        {state === "done" && <CheckCircle2 className="h-7 w-7 text-success animate-scale-in" />}
        {state === "error" && <XCircle className="h-7 w-7 text-destructive animate-scale-in" />}
        {state === "idle" && (
          <div className="w-3 h-3 rounded-full bg-muted-foreground/20" />
        )}
      </div>
    </div>
  );
};

const ClaimProcessing = () => {
  const { state, crossValidate, sendReport } = useClaim();
  const navigate = useNavigate();
  const [cvStatus, setCvStatus] = useState<StepState>("idle");
  const [reportStatus, setReportStatus] = useState<StepState>("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!state.claimantType) navigate("/claim/start", { replace: true });
    else if (!state.claimType) navigate("/claim/type", { replace: true });
    else if (!state.details) navigate("/claim/details", { replace: true });
    else if (!state.aadhar) navigate("/claim/id-verify", { replace: true });
    else if (!state.narrative) navigate("/claim/narrative", { replace: true });
    else if (!state.documents) navigate("/claim/documents", { replace: true });
  }, [navigate, state.aadhar, state.claimType, state.claimantType, state.details, state.documents, state.narrative]);

  const hasRun = useRef(false);

  useEffect(() => {
    if (hasRun.current) return;
    hasRun.current = true;

    const run = async () => {
      setError(null);
      try {
        setCvStatus("working");
        await crossValidate();
        setCvStatus("done");

        setReportStatus("working");
        await sendReport();
        setReportStatus("done");
      } catch (err) {
        setCvStatus((s) => (s === "working" ? "error" : s));
        setReportStatus((s) => (s === "working" ? "error" : s));
        setError(err instanceof Error ? err.message : "Processing failed");
      }
    };
    void run();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const report = state.report;
  const isComplete = reportStatus === "done";

  const confidencePercent = report ? (report.confidence * 100).toFixed(1) : "0";
  const confidenceSize = 120;
  const confidenceStroke = 6;
  const confidenceRadius = (confidenceSize - confidenceStroke) / 2;
  const confidenceCircumference = 2 * Math.PI * confidenceRadius;
  const confidenceOffset = report
    ? confidenceCircumference * (1 - report.confidence)
    : confidenceCircumference;

  return (
    <ClaimLayout title="Claim Processing" subtitle="Validating your claim and generating the final report.">
      <div className="space-y-6">
        {/* Processing steps */}
        <Card className="shadow-premium border-0">
          <CardContent className="p-6 md:p-8">
            {error && (
              <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4 mb-6">
                <p className="text-sm text-destructive font-medium">{error}</p>
              </div>
            )}

            <div className="flex flex-col md:flex-row items-center justify-center gap-8 md:gap-16 py-6">
              {/* Step 1: Cross-validation */}
              <div className="flex flex-col items-center gap-4">
                <AnimatedCircle state={cvStatus} />
                <div className="text-center">
                  <div className="flex items-center gap-2 justify-center mb-1">
                    <ShieldCheck className="h-4 w-4 text-accent" />
                    <p className="text-sm font-bold text-foreground">Cross-Validation</p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {cvStatus === "working" && "Analyzing claim data..."}
                    {cvStatus === "done" && "Validation complete"}
                    {cvStatus === "error" && "Validation failed"}
                    {cvStatus === "idle" && "Waiting..."}
                  </p>
                </div>
              </div>

              {/* Connector */}
              <div className="hidden md:block w-20 h-0.5 rounded-full bg-gradient-to-r from-accent/40 to-accent/10" />
              <div className="md:hidden h-8 w-0.5 rounded-full bg-gradient-to-b from-accent/40 to-accent/10" />

              {/* Step 2: Send report */}
              <div className="flex flex-col items-center gap-4">
                <AnimatedCircle state={reportStatus} delay={200} />
                <div className="text-center">
                  <div className="flex items-center gap-2 justify-center mb-1">
                    <Mail className="h-4 w-4 text-accent" />
                    <p className="text-sm font-bold text-foreground">Send Report</p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {reportStatus === "working" && "Generating report..."}
                    {reportStatus === "done" && "Report sent successfully"}
                    {reportStatus === "error" && "Report sending failed"}
                    {reportStatus === "idle" && "Waiting..."}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Report result */}
        {report && (
          <Card className="shadow-premium border-0 animate-fade-in-up overflow-hidden">
            <div className="gradient-primary p-6 flex items-center gap-4">
              <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center">
                <Award className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="text-white text-lg font-bold font-display">Claim Decision</h3>
                <p className="text-white/60 text-xs">Your claim has been processed</p>
              </div>
            </div>
            <CardContent className="p-6 md:p-8">
              <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Confidence circle */}
                <div className="flex flex-col items-center gap-3 shrink-0">
                  <div className="relative" style={{ width: confidenceSize, height: confidenceSize }}>
                    <svg
                      width={confidenceSize}
                      height={confidenceSize}
                      viewBox={`0 0 ${confidenceSize} ${confidenceSize}`}
                      className="transform -rotate-90"
                    >
                      <defs>
                        <linearGradient id="conf-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="hsl(217 91% 30%)" />
                          <stop offset="50%" stopColor="hsl(217 91% 50%)" />
                          <stop offset="100%" stopColor="hsl(199 89% 48%)" />
                        </linearGradient>
                      </defs>
                      <circle
                        cx={confidenceSize / 2}
                        cy={confidenceSize / 2}
                        r={confidenceRadius}
                        fill="none"
                        stroke="hsl(var(--muted))"
                        strokeWidth={confidenceStroke}
                        opacity={0.2}
                      />
                      <circle
                        cx={confidenceSize / 2}
                        cy={confidenceSize / 2}
                        r={confidenceRadius}
                        fill="none"
                        stroke="url(#conf-gradient)"
                        strokeWidth={confidenceStroke}
                        strokeLinecap="round"
                        strokeDasharray={confidenceCircumference}
                        strokeDashoffset={confidenceOffset}
                        style={{
                          transition: "stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1)",
                        }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-bold text-gradient font-display">
                        {confidencePercent}%
                      </span>
                      <span className="text-[9px] uppercase tracking-wider font-semibold text-muted-foreground">
                        Confidence
                      </span>
                    </div>
                  </div>
                </div>

                {/* Decision details */}
                <div className="flex-1 space-y-5 w-full">
                  <div className="grid sm:grid-cols-2 gap-4">
                    <div className="rounded-2xl bg-accent/5 border border-accent/15 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <TrendingUp className="h-4 w-4 text-accent" />
                        <p className="text-[10px] uppercase tracking-wider font-semibold text-accent">
                          Decision
                        </p>
                      </div>
                      <p className="text-lg font-bold text-foreground font-display">
                        {report.decision}
                      </p>
                    </div>
                    <div className="rounded-2xl bg-success/5 border border-success/15 p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Send className="h-4 w-4 text-success" />
                        <p className="text-[10px] uppercase tracking-wider font-semibold text-success">
                          Report Sent To
                        </p>
                      </div>
                      <p className="text-sm font-bold text-foreground break-all">
                        {report.recipient}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    A detailed report has been sent to the email address above. You can review the
                    claim status and details from your dashboard at any time.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate(-1)}
            className="gap-2 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </Button>
          <Button
            onClick={() => navigate("/dashboard")}
            disabled={!isComplete}
            className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
          >
            <LayoutDashboard className="h-4 w-4" />
            Go to Dashboard
          </Button>
        </div>
      </div>
    </ClaimLayout>
  );
};

export default ClaimProcessing;
