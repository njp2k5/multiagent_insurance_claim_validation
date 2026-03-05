import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useClaim } from "@/contexts/ClaimContext";
import {
  Upload,
  ArrowLeft,
  ArrowRight,
  Loader2,
  CheckCircle2,
  X,
  FileText,
  MessageCircle,
  Send,
  History,
  Bot,
  User,
  Sparkles,
} from "lucide-react";
import ClaimLayout from "@/components/ClaimLayout";
import { terminalLog } from "@/lib/terminalLog";

const docOptions = ["Medical report", "Prescription", "FIR", "Bills", "Other"];

const ClaimDocuments = () => {
  const { state, uploadDocuments, initChat, sendChatMessage, fetchChatHistory } = useClaim();
  const navigate = useNavigate();

  const [files, setFiles] = useState<(File | null)[]>([null, null]);
  const [types, setTypes] = useState<string[]>([docOptions[0], docOptions[1]]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validation, setValidation] = useState(state.documents?.validation);
  const [extraction, setExtraction] = useState(state.documents?.extraction);

  // Chat state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatMessages, setChatMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const chatContainerRef = useRef<HTMLDivElement | null>(null);
  const chatInputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    terminalLog("ClaimDocuments", "Mounted — claim_id:", state.claimId);
    if (!state.claimantType) navigate("/claim/start", { replace: true });
    else if (!state.claimType) navigate("/claim/type", { replace: true });
    else if (!state.details) navigate("/claim/details", { replace: true });
    else if (!state.aadhar) navigate("/claim/id-verify", { replace: true });
    else if (!state.narrative) navigate("/claim/narrative", { replace: true });
  }, [navigate, state.aadhar, state.claimType, state.claimantType, state.details, state.narrative]);

  const onFileChange = (index: number, file: File | null) => {
    setFiles((prev) => prev.map((f, i) => (i === index ? file : f)));
  };

  const handleSubmit = async () => {
    const chosen = files.filter(Boolean) as File[];
    if (!chosen.length) {
      setError("Please upload at least one document (max 2).");
      return;
    }
    terminalLog("ClaimDocuments", "Uploading documents — claim_id:", state.claimId);
    setIsSubmitting(true);
    setError(null);
    try {
      const { validation: val, extraction: ext } = await uploadDocuments(chosen);
      setValidation(val);
      setExtraction(ext);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document upload failed");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Chat auto-scroll
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatMessages, chatOpen]);

  // Chat bootstrap
  useEffect(() => {
    const bootstrap = async () => {
      if (!chatOpen) return;
      setChatError(null);
      try {
        await initChat();
        const hist = state.chat?.history || [];
        const initial: { role: "user" | "assistant"; text: string }[] = [];
        hist.forEach((h) => {
          initial.push({ role: "user", text: h.user });
          initial.push({ role: "assistant", text: h.assistant });
        });
        if (state.chat?.lastReply) {
          initial.push({ role: "assistant", text: state.chat.lastReply });
        }
        if (initial.length) setChatMessages(initial);
      } catch (err) {
        setChatError(err instanceof Error ? err.message : "Unable to start chat");
      }
    };
    void bootstrap();
  }, [chatOpen, initChat, state.chat?.history, state.chat?.lastReply]);

  const handleSendMessage = async () => {
    const msg = chatInput.trim();
    if (!msg) return;
    setChatLoading(true);
    setChatError(null);
    setChatMessages((prev) => [...prev, { role: "user", text: msg }]);
    setChatInput("");
    try {
      await initChat();
      const reply = await sendChatMessage(msg);
      setChatMessages((prev) => [...prev, { role: "assistant", text: reply }]);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to send message");
    } finally {
      setChatLoading(false);
    }
  };

  const handleLoadHistory = async () => {
    setChatError(null);
    try {
      await initChat();
      const history = await fetchChatHistory();
      const mapped = history.flatMap((h) => [
        { role: "user" as const, text: h.user },
        { role: "assistant" as const, text: h.assistant },
      ]);
      setChatMessages(mapped);
    } catch (err) {
      setChatError(err instanceof Error ? err.message : "Failed to load history");
    }
  };

  const statusColor = validation?.agent_status === "PASS" ? "text-success" : "text-destructive";
  const statusBg = validation?.agent_status === "PASS" ? "bg-success/5 border-success/20" : "bg-destructive/5 border-destructive/20";

  return (
    <ClaimLayout title="Upload Documents" subtitle="Upload supporting documents for validation and extraction.">
      <div className="space-y-6">
        <Card className="shadow-premium border-0">
          <CardContent className="p-6 md:p-8 space-y-6">
            {error && (
              <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-4">
                <p className="text-sm text-destructive font-medium">{error}</p>
              </div>
            )}

            {/* Document upload slots */}
            <div className="grid md:grid-cols-2 gap-5">
              {[0, 1].map((idx) => (
                <div
                  key={idx}
                  className="rounded-2xl border border-border/60 p-5 space-y-4 bg-white hover:shadow-sm transition-shadow"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center">
                      <FileText className="h-3.5 w-3.5 text-accent" />
                    </div>
                    <span className="text-sm font-semibold text-foreground">Document {idx + 1}</span>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      Type
                    </Label>
                    <Select
                      value={types[idx]}
                      onValueChange={(val) => setTypes((prev) => prev.map((t, i) => (i === idx ? val : t)))}
                    >
                      <SelectTrigger className="h-10 bg-muted/30 border-border/60">
                        <SelectValue placeholder="Choose type" />
                      </SelectTrigger>
                      <SelectContent>
                        {docOptions.map((opt) => (
                          <SelectItem key={opt} value={opt}>{opt}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                      File
                    </Label>
                    {files[idx] ? (
                      <div className="flex items-center gap-3 p-3 rounded-xl bg-success/5 border border-success/20">
                        <FileText className="h-4 w-4 text-success shrink-0" />
                        <span className="text-xs font-medium text-foreground truncate flex-1">
                          {files[idx]?.name}
                        </span>
                        <button
                          onClick={() => onFileChange(idx, null)}
                          className="w-6 h-6 rounded-full bg-muted hover:bg-muted-foreground/10 flex items-center justify-center transition-colors shrink-0"
                        >
                          <X className="h-3 w-3 text-muted-foreground" />
                        </button>
                      </div>
                    ) : (
                      <label className="flex items-center gap-3 p-3 rounded-xl border-2 border-dashed border-border/60 hover:border-accent/40 cursor-pointer transition-colors">
                        <Upload className="h-4 w-4 text-muted-foreground" />
                        <span className="text-xs text-muted-foreground">Click to upload</span>
                        <input
                          type="file"
                          accept=".pdf,image/*"
                          className="hidden"
                          onChange={(e) => onFileChange(idx, e.target.files?.[0] ?? null)}
                        />
                      </label>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Upload button */}
            <div className="flex items-center justify-between pt-2">
              <Button
                variant="ghost"
                onClick={() => navigate(-1)}
                className="gap-2 text-muted-foreground hover:text-foreground"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              <Button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-4 w-4" />
                    Upload & Validate
                  </>
                )}
              </Button>
            </div>

            {/* Validation result */}
            {validation && (
              <div className={"rounded-2xl border p-6 space-y-3 animate-scale-in " + statusBg}>
                <div className="flex items-center gap-3">
                  <CheckCircle2 className={"h-5 w-5 " + statusColor} />
                  <p className={"font-bold text-sm " + statusColor}>
                    Validation: {validation.agent_status || "N/A"}
                  </p>
                </div>
                <p className="text-sm text-foreground/80 whitespace-pre-line leading-relaxed">
                  {validation.summary}
                </p>
              </div>
            )}

            {/* Extraction result */}
            {extraction && (
              <div className="rounded-2xl bg-accent/5 border border-accent/15 p-6 animate-scale-in">
                <p className="text-xs font-semibold uppercase tracking-wider text-accent mb-3">
                  Extracted Information
                </p>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="bg-white rounded-xl p-3 shadow-sm">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">
                      Name
                    </p>
                    <p className="text-sm font-bold text-foreground">{extraction.document_name}</p>
                  </div>
                  <div className="bg-white rounded-xl p-3 shadow-sm">
                    <p className="text-[10px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">
                      Age
                    </p>
                    <p className="text-sm font-bold text-foreground">{extraction.document_age}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Continue button */}
            {(validation || extraction) && (
              <div className="flex justify-end pt-2">
                <Button
                  onClick={() => navigate("/claim/processing")}
                  className="gap-2 gradient-primary hover:opacity-90 shadow-lg shadow-primary/15 px-8"
                >
                  Continue to Processing
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Chat Assistant */}

      {/* Floating trigger button */}
      {!chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-2xl gradient-primary text-white shadow-xl shadow-primary/25 flex items-center justify-center hover:scale-105 active:scale-95 transition-transform z-50"
        >
          <MessageCircle className="h-6 w-6" />
        </button>
      )}

      {/* Chat panel */}
      {chatOpen && (
        <div className="fixed bottom-6 right-6 w-[400px] max-h-[75vh] bg-white border border-border/60 shadow-2xl rounded-3xl flex flex-col z-50 animate-scale-in overflow-hidden">
          {/* Chat header */}
          <div className="gradient-primary p-4 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-white/15 backdrop-blur flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-white" />
              </div>
              <div>
                <h3 className="text-white text-sm font-bold">Claim Assistant</h3>
                <p className="text-white/50 text-[10px]">AI-powered support</p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              <button
                onClick={handleLoadHistory}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                title="Load history"
              >
                <History className="h-3.5 w-3.5 text-white" />
              </button>
              <button
                onClick={() => setChatOpen(false)}
                className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors"
                title="Close"
              >
                <X className="h-3.5 w-3.5 text-white" />
              </button>
            </div>
          </div>

          {/* Chat messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 min-h-[200px] max-h-[400px] bg-gradient-to-b from-muted/20 to-white"
          >
            {chatMessages.length === 0 && !chatError && (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center mb-3">
                  <Bot className="h-6 w-6 text-accent" />
                </div>
                <p className="text-sm font-semibold text-foreground mb-1">How can I help?</p>
                <p className="text-xs text-muted-foreground max-w-[240px]">
                  Ask anything about your claim, documents, or the process.
                </p>
              </div>
            )}

            {chatMessages.map((m, idx) => (
              <div
                key={idx}
                className={"flex gap-2.5 animate-fade-in " + (m.role === "user" ? "justify-end" : "justify-start")}
              >
                {m.role === "assistant" && (
                  <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center shrink-0 mt-0.5">
                    <Bot className="h-3.5 w-3.5 text-accent" />
                  </div>
                )}
                <div
                  className={"max-w-[75%] text-sm rounded-2xl px-4 py-2.5 leading-relaxed " + (
                    m.role === "user"
                      ? "gradient-primary text-white rounded-br-md"
                      : "bg-muted/60 text-foreground rounded-bl-md"
                  )}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>
                {m.role === "user" && (
                  <div className="w-7 h-7 rounded-lg bg-primary/10 flex items-center justify-center shrink-0 mt-0.5">
                    <User className="h-3.5 w-3.5 text-primary" />
                  </div>
                )}
              </div>
            ))}

            {chatLoading && (
              <div className="flex gap-2.5 animate-fade-in">
                <div className="w-7 h-7 rounded-lg bg-accent/10 flex items-center justify-center shrink-0">
                  <Bot className="h-3.5 w-3.5 text-accent" />
                </div>
                <div className="bg-muted/60 rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              </div>
            )}

            {chatError && (
              <div className="rounded-xl bg-destructive/10 border border-destructive/20 p-3">
                <p className="text-xs text-destructive">{chatError}</p>
              </div>
            )}
          </div>

          {/* Chat input */}
          <div className="p-3 border-t border-border/60 bg-white shrink-0">
            <div className="flex items-end gap-2">
              <textarea
                ref={chatInputRef}
                rows={1}
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                placeholder="Type your message..."
                className="flex-1 resize-none rounded-xl border border-border/60 bg-muted/30 px-4 py-2.5 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent/20 focus:border-accent/40 transition-all min-h-[40px] max-h-[100px]"
              />
              <button
                disabled={!chatInput.trim() || chatLoading}
                onClick={handleSendMessage}
                className="w-10 h-10 rounded-xl gradient-primary text-white flex items-center justify-center shrink-0 hover:opacity-90 disabled:opacity-40 transition-all shadow-lg shadow-primary/15"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </ClaimLayout>
  );
};

export default ClaimDocuments;
