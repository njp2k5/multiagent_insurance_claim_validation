import { ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Shield, ChevronRight, Zap } from "lucide-react";

const steps = [
  { path: "/claim/start", label: "Claimant", shortLabel: "Start" },
  { path: "/claim/type", label: "Insurance Type", shortLabel: "Type" },
  { path: "/claim/details", label: "Claim Details", shortLabel: "Details" },
  { path: "/claim/id-verify", label: "ID Verification", shortLabel: "Verify" },
  { path: "/claim/narrative", label: "Narrative", shortLabel: "Story" },
  { path: "/claim/documents", label: "Documents", shortLabel: "Docs" },
  { path: "/claim/processing", label: "Processing", shortLabel: "Result" },
];

interface ClaimLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

const CircularProgress = ({
  step,
  total,
  size = 44,
}: {
  step: number;
  total: number;
  size?: number;
}) => {
  const strokeWidth = 3;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = step / total;
  const offset = circumference - progress * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(217 91% 50% / 0.12)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="hsl(217 91% 50%)" />
            <stop offset="100%" stopColor="hsl(199 89% 48%)" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute text-xs font-bold text-primary">
        {step}/{total}
      </span>
    </div>
  );
};

const ClaimLayout = ({ children, title, subtitle }: ClaimLayoutProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const currentIndex = steps.findIndex((s) => s.path === location.pathname);
  const currentStep = currentIndex >= 0 ? currentIndex + 1 : 1;

  return (
    <div className="min-h-screen bg-background">
      {/* Premium Header */}
      <header className="gradient-primary text-white relative overflow-hidden">
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
        </div>
        <div className="container mx-auto px-6 py-4 relative z-10">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate("/dashboard")}
              className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
            >
              <div className="w-9 h-9 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <div>
                <span className="text-base font-bold tracking-tight block leading-none">
                  Intelli<span className="text-sky-300">claim</span>
                </span>
                <span className="text-[10px] text-white/50 tracking-widest uppercase">
                  Multi-Agent System
                </span>
              </div>
            </button>
            <CircularProgress step={currentStep} total={steps.length} />
          </div>
        </div>
      </header>

      {/* Step Progress Bar */}
      <div className="bg-white border-b border-border/60 sticky top-0 z-40 shadow-sm">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-1 py-3 overflow-x-auto scrollbar-hide">
            {steps.map((step, index) => {
              const isCompleted = index < currentIndex;
              const isCurrent = index === currentIndex;
              const isFuture = index > currentIndex;

              return (
                <div key={step.path} className="flex items-center shrink-0">
                  {index > 0 && (
                    <ChevronRight
                      className={`h-3.5 w-3.5 mx-1 shrink-0 ${
                        isCompleted ? "text-accent" : "text-border"
                      }`}
                    />
                  )}
                  <button
                    onClick={() => isCompleted && navigate(step.path)}
                    disabled={isFuture || isCurrent}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
                      isCurrent
                        ? "bg-accent text-white shadow-md shadow-accent/25"
                        : isCompleted
                        ? "bg-accent/10 text-accent hover:bg-accent/20 cursor-pointer"
                        : "bg-muted/60 text-muted-foreground"
                    }`}
                  >
                    <span
                      className={`flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold ${
                        isCurrent
                          ? "bg-white/25 text-white"
                          : isCompleted
                          ? "bg-accent text-white"
                          : "bg-muted-foreground/15 text-muted-foreground"
                      }`}
                    >
                      {isCompleted ? "✓" : index + 1}
                    </span>
                    <span className="hidden sm:inline">{step.label}</span>
                    <span className="sm:hidden">{step.shortLabel}</span>
                  </button>
                </div>
              );
            })}
          </div>
          {/* Animated progress line */}
          <div className="h-0.5 bg-muted/60 rounded-full overflow-hidden -mt-0.5">
            <div
              className="h-full gradient-accent rounded-full transition-all duration-700 ease-out"
              style={{ width: `${(currentStep / steps.length) * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Page Content */}
      <main className="container mx-auto px-6 py-8 max-w-4xl animate-fade-in-up">
        {/* Title Section */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-foreground">{title}</h1>
          {subtitle && (
            <p className="text-muted-foreground mt-1.5 text-sm md:text-base">{subtitle}</p>
          )}
        </div>
        {children}
      </main>
    </div>
  );
};

export default ClaimLayout;
