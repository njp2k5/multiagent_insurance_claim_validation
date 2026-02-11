import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useClaim } from "@/contexts/ClaimContext";
import { Upload, ArrowLeft, ArrowRight, Loader2, CheckCircle2, FileText, X } from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";

const ClaimAadhar = () => {
  const { state, verifyAadhar } = useClaim();
  const navigate = useNavigate();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState(state.aadhar);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    if (!state.claimantType) navigate("/claim/start", { replace: true });
    else if (!state.claimType) navigate("/claim/type", { replace: true });
    else if (!state.details) navigate("/claim/details", { replace: true });
  }, [navigate, state.claimType, state.claimantType, state.details]);

  const handleUpload = async () => {
    if (!file) {
      setError("Please select an Aadhaar file to upload");
      return;
    }
    setIsSubmitting(true);
    setError(null);
    try {
      const data = await verifyAadhar(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") setDragActive(true);
    else if (e.type === "dragleave") setDragActive(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) setFile(droppedFile);
  };

  return (
    <ClaimLayout title="Identity Verification" subtitle="Upload your Aadhaar document for identity verification.">
      <Card className="shadow-premium border-0">
        <CardContent className="p-6 md:p-8 space-y-6">
          {error && (
            <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4">
              <p className="text-sm text-destructive font-medium">{error}</p>
            </div>
          )}

          {/* Drop zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => inputRef.current?.click()}
            className={`relative border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center gap-4 cursor-pointer transition-all duration-300 ${
              dragActive
                ? "border-accent bg-accent/5 scale-[1.01]"
                : file
                ? "border-success/40 bg-success/5"
                : "border-border/60 hover:border-accent/40 hover:bg-accent/[0.02]"
            }`}
          >
            <input
              ref={inputRef}
              type="file"
              accept=".pdf,image/*"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <>
                <div className="w-14 h-14 rounded-2xl bg-success/10 flex items-center justify-center">
                  <FileText className="h-7 w-7 text-success" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-semibold text-foreground">{file.name}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {(file.size / 1024).toFixed(1)} KB • Click to change
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                    setResult(undefined);
                  }}
                  className="absolute top-4 right-4 w-8 h-8 rounded-full bg-muted hover:bg-muted-foreground/10 flex items-center justify-center transition-colors"
                >
                  <X className="h-4 w-4 text-muted-foreground" />
                </button>
              </>
            ) : (
              <>
                <div className="w-14 h-14 rounded-2xl bg-accent/10 flex items-center justify-center">
                  <Upload className="h-7 w-7 text-accent" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-semibold text-foreground">
                    Drop your Aadhaar here or click to browse
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Accepts PDF and image files
                  </p>
                </div>
              </>
            )}
          </div>

          {/* Verify button */}
          {file && !result && (
            <div className="flex justify-center">
              <Button
                onClick={handleUpload}
                disabled={isSubmitting}
                className="gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8 gap-2"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4" />
                    Upload & Verify
                  </>
                )}
              </Button>
            </div>
          )}

          {/* Verification result */}
          {result && (
            <div className="rounded-2xl bg-success/5 border border-success/20 p-6 animate-scale-in">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-success/10 flex items-center justify-center">
                  <CheckCircle2 className="h-5 w-5 text-success" />
                </div>
                <div>
                  <p className="font-bold text-success text-sm">Identity Verified</p>
                  <p className="text-xs text-muted-foreground">Aadhaar details extracted successfully</p>
                </div>
              </div>
              <div className="grid sm:grid-cols-3 gap-4">
                <div className="bg-white rounded-xl p-3 shadow-sm">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">
                    Aadhaar Number
                  </p>
                  <p className="text-sm font-bold text-foreground">{result.aadhaar_numbers?.[0]}</p>
                </div>
                <div className="bg-white rounded-xl p-3 shadow-sm">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">
                    Name
                  </p>
                  <p className="text-sm font-bold text-foreground">{result.aadhaar_name}</p>
                </div>
                <div className="bg-white rounded-xl p-3 shadow-sm">
                  <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">
                    Age
                  </p>
                  <p className="text-sm font-bold text-foreground">{result.aadhaar_age}</p>
                </div>
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-4 border-t border-border/60">
            <Button
              variant="ghost"
              onClick={() => navigate("/claim/details")}
              className="gap-2 text-muted-foreground hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Button>
            <Button
              onClick={() => navigate("/claim/narrative")}
              disabled={!result}
              className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
            >
              Continue
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </ClaimLayout>
  );
};

export default ClaimAadhar;