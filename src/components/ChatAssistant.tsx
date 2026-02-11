import { useState, useRef, useEffect, FormEvent } from "react";
import { MessageCircle, X, Send, History, ArrowLeft, Loader2, Bot, User } from "lucide-react";
import { useClaim } from "@/contexts/ClaimContext";
import { Button } from "@/components/ui/button";

type ChatMessage = {
  role: "user" | "assistant" | "system";
  content: string;
};

const ChatAssistant = () => {
  const { state, initChat, sendChatMessage, fetchChatHistory } = useClaim();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [initializing, setInitializing] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyMessages, setHistoryMessages] = useState<{ user: string; assistant: string }[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, historyMessages]);

  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open, showHistory]);

  const handleOpen = async () => {
    setOpen(true);
    if (!state.chat?.sessionToken) {
      setInitializing(true);
      try {
        await initChat();
        setMessages([
          {
            role: "system",
            content:
              state.chat?.lastReply ||
              "Chat session initialized. You can now ask questions about your claim.",
          },
        ]);
      } catch (err: any) {
        setMessages([
          { role: "system", content: err.message || "Failed to initialize chat. Please try again." },
        ]);
      } finally {
        setInitializing(false);
      }
    }
  };

  // Re-sync the welcome message after state updates from initChat
  useEffect(() => {
    if (open && state.chat?.sessionToken && messages.length === 0) {
      setMessages([
        {
          role: "system",
          content: state.chat.lastReply || "Chat session initialized. You can now ask questions about your claim.",
        },
      ]);
    }
  }, [open, state.chat?.sessionToken, state.chat?.lastReply]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);

    try {
      const reply = await sendChatMessage(text);
      setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: err.message || "Something went wrong. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchHistory = async () => {
    setShowHistory(true);
    setHistoryLoading(true);
    try {
      const history = await fetchChatHistory();
      setHistoryMessages(history);
    } catch (err: any) {
      setHistoryMessages([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setShowHistory(false);
  };

  // Don't render if there's no claim in progress
  if (!state.claimId) return null;

  return (
    <>
      {/* Floating Action Button */}
      {!open && (
        <button
          onClick={handleOpen}
          className="fixed bottom-6 right-6 z-50 flex items-center justify-center w-14 h-14 rounded-full gradient-primary text-white shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105 animate-scale-in group"
          aria-label="Open chat assistant"
        >
          <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
          {/* Pulse ring */}
          <span className="absolute inset-0 rounded-full gradient-primary opacity-30 animate-ping" />
        </button>
      )}

      {/* Chat Window */}
      {open && (
        <div className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-2rem)] h-[540px] max-h-[calc(100vh-4rem)] flex flex-col rounded-2xl shadow-card-hover border border-border bg-card overflow-hidden animate-scale-in">
          {/* Header */}
          <div className="gradient-primary text-white px-4 py-3 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2.5">
              {showHistory && (
                <button
                  onClick={() => setShowHistory(false)}
                  className="p-1 rounded-lg hover:bg-white/15 transition-colors"
                  aria-label="Back to chat"
                >
                  <ArrowLeft className="h-4 w-4" />
                </button>
              )}
              <div className="w-8 h-8 rounded-lg bg-white/15 backdrop-blur flex items-center justify-center">
                <Bot className="h-4.5 w-4.5" />
              </div>
              <div>
                <p className="text-sm font-semibold leading-none">
                  {showHistory ? "Chat History" : "Claim Assistant"}
                </p>
                <p className="text-[10px] text-white/60 mt-0.5">
                  {showHistory
                    ? "Previous conversations"
                    : state.chat?.sessionToken
                    ? "Online"
                    : "Connecting…"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-1">
              {!showHistory && state.chat?.sessionToken && (
                <button
                  onClick={handleFetchHistory}
                  className="p-1.5 rounded-lg hover:bg-white/15 transition-colors"
                  aria-label="View chat history"
                  title="Chat history"
                >
                  <History className="h-4 w-4" />
                </button>
              )}
              <button
                onClick={handleClose}
                className="p-1.5 rounded-lg hover:bg-white/15 transition-colors"
                aria-label="Close chat"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Body */}
          {showHistory ? (
            /* History View */
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/30">
              {historyLoading ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground">
                  <Loader2 className="h-6 w-6 animate-spin text-accent" />
                  <p className="text-xs">Loading history…</p>
                </div>
              ) : historyMessages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground">
                  <History className="h-8 w-8 opacity-40" />
                  <p className="text-xs">No chat history yet</p>
                </div>
              ) : (
                historyMessages.map((entry, i) => (
                  <div key={i} className="space-y-2">
                    {/* User message */}
                    <div className="flex justify-end">
                      <div className="flex items-end gap-1.5 max-w-[85%]">
                        <div className="bg-accent text-accent-foreground px-3 py-2 rounded-2xl rounded-br-md text-sm leading-relaxed">
                          {entry.user}
                        </div>
                        <div className="w-6 h-6 rounded-full bg-accent/15 flex items-center justify-center shrink-0">
                          <User className="h-3 w-3 text-accent" />
                        </div>
                      </div>
                    </div>
                    {/* Assistant message */}
                    <div className="flex justify-start">
                      <div className="flex items-end gap-1.5 max-w-[85%]">
                        <div className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center shrink-0">
                          <Bot className="h-3 w-3 text-white" />
                        </div>
                        <div className="bg-card border border-border px-3 py-2 rounded-2xl rounded-bl-md text-sm leading-relaxed shadow-sm">
                          {entry.assistant}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            /* Chat View */
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-muted/30">
              {initializing ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 text-muted-foreground">
                  <Loader2 className="h-6 w-6 animate-spin text-accent" />
                  <p className="text-xs">Initializing chat session…</p>
                </div>
              ) : (
                messages.map((msg, i) => {
                  if (msg.role === "system") {
                    return (
                      <div key={i} className="flex justify-start">
                        <div className="flex items-end gap-1.5 max-w-[85%]">
                          <div className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center shrink-0">
                            <Bot className="h-3 w-3 text-white" />
                          </div>
                          <div className="bg-card border border-border px-3 py-2 rounded-2xl rounded-bl-md text-sm leading-relaxed shadow-sm text-muted-foreground italic">
                            {msg.content}
                          </div>
                        </div>
                      </div>
                    );
                  }

                  if (msg.role === "user") {
                    return (
                      <div key={i} className="flex justify-end">
                        <div className="flex items-end gap-1.5 max-w-[85%]">
                          <div className="bg-accent text-accent-foreground px-3 py-2 rounded-2xl rounded-br-md text-sm leading-relaxed">
                            {msg.content}
                          </div>
                          <div className="w-6 h-6 rounded-full bg-accent/15 flex items-center justify-center shrink-0">
                            <User className="h-3 w-3 text-accent" />
                          </div>
                        </div>
                      </div>
                    );
                  }

                  // assistant
                  return (
                    <div key={i} className="flex justify-start">
                      <div className="flex items-end gap-1.5 max-w-[85%]">
                        <div className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center shrink-0">
                          <Bot className="h-3 w-3 text-white" />
                        </div>
                        <div className="bg-card border border-border px-3 py-2 rounded-2xl rounded-bl-md text-sm leading-relaxed shadow-sm">
                          {msg.content}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}

              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-end gap-1.5">
                    <div className="w-6 h-6 rounded-full gradient-primary flex items-center justify-center shrink-0">
                      <Bot className="h-3 w-3 text-white" />
                    </div>
                    <div className="bg-card border border-border px-4 py-2.5 rounded-2xl rounded-bl-md shadow-sm">
                      <div className="flex gap-1">
                        <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:0ms]" />
                        <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:150ms]" />
                        <span className="w-1.5 h-1.5 bg-muted-foreground/50 rounded-full animate-bounce [animation-delay:300ms]" />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Input Area (only in chat view) */}
          {!showHistory && (
            <form
              onSubmit={handleSend}
              className="shrink-0 border-t border-border bg-card px-3 py-2.5 flex items-center gap-2"
            >
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about your claim…"
                disabled={loading || initializing}
                className="flex-1 bg-muted/50 border border-border rounded-xl px-3 py-2 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent/40 disabled:opacity-50 transition-all"
              />
              <Button
                type="submit"
                size="icon"
                disabled={!input.trim() || loading || initializing}
                className="shrink-0 h-9 w-9 rounded-xl gradient-primary text-white hover:opacity-90 disabled:opacity-40"
              >
                <Send className="h-4 w-4" />
              </Button>
            </form>
          )}
        </div>
      )}
    </>
  );
};

export default ChatAssistant;
