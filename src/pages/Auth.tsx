import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Loader2, Zap, Shield, Brain, Lock, Eye, EyeOff } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Auth = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { signIn, signUp } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) return;
    setLoading(true);
    try {
      if (isSignUp) {
        await signUp(username.trim(), password);
        toast({ title: "Account created!", description: "You can now sign in." });
        setIsSignUp(false);
        setPassword("");
      } else {
        await signIn(username.trim(), password);
        navigate("/dashboard");
      }
    } catch (err: any) {
      toast({
        title: isSignUp ? "Sign up failed" : "Sign in failed",
        description: err.message,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Panel - Premium Branding */}
      <div className="hidden lg:flex lg:w-[55%] gradient-primary relative overflow-hidden items-center justify-center p-16">
        {/* Decorative elements */}
        <div className="absolute inset-0">
          <div className="absolute top-20 right-20 w-72 h-72 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute bottom-20 left-10 w-96 h-96 bg-sky-400/[.08] rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-400/5 rounded-full blur-3xl" />
          {/* Grid pattern */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage:
                "linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",
              backgroundSize: "60px 60px",
            }}
          />
        </div>

        <div className="relative z-10 max-w-lg">
          {/* Logo */}
          <div className="flex items-center gap-3 mb-12">
            <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center">
              <Zap className="h-7 w-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white tracking-tight font-sans">
                Intelli<span className="text-sky-300">claim</span>
              </h2>
              <p className="text-[11px] text-white/40 tracking-[0.2em] uppercase font-medium">
                Multi-Agent Validation System
              </p>
            </div>
          </div>

          {/* Main Headline */}
          <h1 className="text-5xl font-bold text-white mb-6 leading-[1.1] tracking-tight">
            AI-Powered
            <br />
            <span className="text-sky-300">Insurance Claim</span>
            <br />
            Validation
          </h1>

          <p className="text-lg text-white/60 leading-relaxed mb-12 max-w-md">
            Experience next-generation claim processing powered by intelligent multi-agent systems.
            Faster decisions, smarter validation.
          </p>

          {/* Feature pills */}
          <div className="flex flex-col gap-4">
            {[
              { icon: Brain, label: "Multi-Agent AI Processing", desc: "Intelligent claim analysis" },
              { icon: Shield, label: "Fraud Detection", desc: "Real-time cross-validation" },
              { icon: Lock, label: "Secure & Compliant", desc: "Enterprise-grade security" },
            ].map((feature) => (
              <div
                key={feature.label}
                className="flex items-center gap-4 p-4 rounded-2xl bg-white/[0.06] backdrop-blur-sm border border-white/[0.06] hover:bg-white/[0.1] transition-colors duration-300"
              >
                <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center shrink-0">
                  <feature.icon className="h-5 w-5 text-sky-300" />
                </div>
                <div>
                  <p className="text-white text-sm font-semibold">{feature.label}</p>
                  <p className="text-white/40 text-xs">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right Panel - Auth Form */}
      <div className="w-full lg:w-[45%] flex items-center justify-center p-8 bg-background relative">
        <div
          className="absolute inset-0 opacity-[0.015]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, hsl(217 91% 30%) 1px, transparent 0)",
            backgroundSize: "40px 40px",
          }}
        />

        <div className="w-full max-w-[420px] relative z-10">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center gap-2.5 mb-10 justify-center">
            <div className="w-10 h-10 rounded-xl gradient-primary flex items-center justify-center">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-black text-foreground tracking-tight font-sans">
                Intelli<span className="text-accent">claim</span>
              </span>
              <p className="text-[9px] text-muted-foreground tracking-[0.15em] uppercase">
                Multi-Agent System
              </p>
            </div>
          </div>

          <Card className="border-0 shadow-premium">
            <CardHeader className="space-y-2 pb-2 pt-8 px-8">
              <div className="w-12 h-12 rounded-2xl bg-accent/10 flex items-center justify-center mb-2">
                {isSignUp ? (
                  <ArrowRight className="h-5 w-5 text-accent" />
                ) : (
                  <Lock className="h-5 w-5 text-accent" />
                )}
              </div>
              <CardTitle className="text-2xl font-bold tracking-tight">
                {isSignUp ? "Create your account" : "Welcome back"}
              </CardTitle>
              <CardDescription className="text-sm">
                {isSignUp
                  ? "Join Intelliclaim to get started with AI-powered claims"
                  : "Sign in to access your claims dashboard"}
              </CardDescription>
            </CardHeader>
            <CardContent className="px-8 pb-8 pt-4">
              <form onSubmit={handleSubmit} className="space-y-5">
                <div className="space-y-2">
                  <Label
                    htmlFor="username"
                    className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                  >
                    Email / Username
                  </Label>
                  <Input
                    id="username"
                    type="text"
                    placeholder="you@example.com"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    className="h-12 px-4 bg-muted/40 border-border/60 focus:bg-white transition-colors"
                  />
                </div>
                <div className="space-y-2">
                  <Label
                    htmlFor="password"
                    className="text-xs font-semibold uppercase tracking-wider text-muted-foreground"
                  >
                    Password
                  </Label>
                  <div className="relative">
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="h-12 px-4 pr-12 bg-muted/40 border-border/60 focus:bg-white transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-12 text-sm font-semibold gradient-primary hover:opacity-90 transition-opacity shadow-lg shadow-primary/20"
                >
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <ArrowRight className="h-4 w-4 mr-2" />
                  )}
                  {isSignUp ? "Create Account" : "Sign In"}
                </Button>
              </form>

              <div className="mt-8 pt-6 border-t border-border/60 text-center text-sm text-muted-foreground">
                {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
                <button
                  onClick={() => {
                    setIsSignUp(!isSignUp);
                    setPassword("");
                  }}
                  className="text-accent font-semibold hover:underline underline-offset-4 transition-colors"
                >
                  {isSignUp ? "Sign in" : "Sign up"}
                </button>
              </div>
            </CardContent>
          </Card>

          <p className="text-center text-[11px] text-muted-foreground/50 mt-6">
            Protected by multi-agent AI validation system
          </p>
        </div>
      </div>
    </div>
  );
};

export default Auth;
