import { useAuth } from "@/contexts/AuthContext";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Zap,
  FileText,
  ShoppingCart,
  ClipboardList,
  History,
  User,
  LogOut,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Shield,
} from "lucide-react";

const Dashboard = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const stats = [
    {
      label: "Active Policies",
      value: "3",
      icon: Shield,
      gradient: "from-blue-500 to-blue-600",
      bg: "bg-blue-50",
      color: "text-blue-600",
    },
    {
      label: "Pending Claims",
      value: "1",
      icon: AlertTriangle,
      gradient: "from-amber-500 to-orange-500",
      bg: "bg-amber-50",
      color: "text-amber-600",
    },
    {
      label: "Resolved Claims",
      value: "7",
      icon: CheckCircle,
      gradient: "from-emerald-500 to-green-500",
      bg: "bg-emerald-50",
      color: "text-emerald-600",
    },
    {
      label: "Total Coverage",
      value: "$250K",
      icon: TrendingUp,
      gradient: "from-violet-500 to-purple-500",
      bg: "bg-violet-50",
      color: "text-violet-600",
    },
  ];

  const actions = [
    {
      title: "Submit a Claim",
      description: "File a new insurance claim quickly with AI-powered multi-agent validation",
      icon: FileText,
      onClick: () => navigate("/claim/start"),
      featured: true,
    },
    {
      title: "Purchase Policy",
      description: "Browse and purchase new insurance policies",
      icon: ShoppingCart,
      onClick: () => {},
    },
    {
      title: "My Policies",
      description: "View and manage your active insurance policies",
      icon: ClipboardList,
      onClick: () => {},
    },
    {
      title: "Claims History",
      description: "Track the status of all your past claims",
      icon: History,
      onClick: () => {},
    },
    {
      title: "My Profile",
      description: "Update your personal information and preferences",
      icon: User,
      onClick: () => {},
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="gradient-primary text-white relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/3 rounded-full translate-y-1/2 -translate-x-1/2" />
        </div>
        <div className="container mx-auto px-6 py-4 relative z-10 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 backdrop-blur flex items-center justify-center">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-black tracking-tight font-sans block leading-none">
                Intelli<span className="text-sky-300">claim</span>
              </span>
              <span className="text-[10px] text-white/40 tracking-[0.15em] uppercase">
                Multi-Agent System
              </span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-white/60 hidden sm:inline">{user?.email}</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                signOut();
                navigate("/");
              }}
              className="text-white/70 hover:text-white hover:bg-white/10"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8 max-w-6xl">
        {/* Welcome */}
        <div className="mb-8 animate-fade-in-up">
          <h1 className="text-3xl font-bold text-foreground">
            Welcome back
            {user?.email ? (
              <span className="text-gradient">, {user.email.split("@")[0]}</span>
            ) : (
              ""
            )}
          </h1>
          <p className="text-muted-foreground mt-1">
            Here's an overview of your insurance portfolio
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          {stats.map((stat, i) => (
            <Card
              key={stat.label}
              className="shadow-premium border-0 hover:shadow-card-hover transition-all duration-500 group overflow-hidden"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <CardContent className="p-5 relative">
                <div className="flex items-center justify-between mb-3">
                  <div className={`w-10 h-10 rounded-xl ${stat.bg} flex items-center justify-center group-hover:scale-110 transition-transform duration-300`}>
                    <stat.icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
                <p className="text-3xl font-bold text-foreground tracking-tight">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-1 font-medium">{stat.label}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-foreground">Quick Actions</h2>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {actions.map((action, i) => (
            <Card
              key={action.title}
              onClick={action.onClick}
              className={`group cursor-pointer transition-all duration-500 overflow-hidden ${
                action.featured
                  ? "gradient-primary text-white md:col-span-2 lg:col-span-1 shadow-lg shadow-primary/15 hover:shadow-xl hover:shadow-primary/25"
                  : "border-border/60 shadow-premium hover:shadow-card-hover hover:border-accent/20"
              }`}
              style={{ animationDelay: `${(i + 4) * 80}ms` }}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center gap-3">
                  <div
                    className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-transform duration-300 group-hover:scale-110 ${
                      action.featured ? "bg-white/15" : "bg-accent/8"
                    }`}
                  >
                    <action.icon
                      className={`h-5 w-5 ${
                        action.featured ? "text-white" : "text-accent"
                      }`}
                    />
                  </div>
                  <CardTitle
                    className={`text-base font-sans font-semibold ${
                      action.featured ? "text-white" : ""
                    }`}
                  >
                    {action.title}
                  </CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <CardDescription
                  className={`text-sm ${action.featured ? "text-white/60" : ""}`}
                >
                  {action.description}
                </CardDescription>
                {action.featured && (
                  <div className="mt-4 flex items-center gap-2 text-sm font-medium text-sky-300 group-hover:gap-3 transition-all duration-300">
                    <span>Start claim</span>
                    <ArrowRight className="h-4 w-4" />
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
