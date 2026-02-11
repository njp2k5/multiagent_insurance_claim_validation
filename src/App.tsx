import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { ClaimProvider } from "@/contexts/ClaimContext";
import ChatAssistant from "@/components/ChatAssistant";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import NotFound from "./pages/NotFound";
import ClaimStart from "./pages/ClaimStart";
import ClaimType from "./pages/ClaimType";
import ClaimDetails from "./pages/ClaimDetails";
import ClaimAadhar from "./pages/ClaimAadhar";
import ClaimNarrative from "./pages/ClaimNarrative";
import ClaimDocuments from "./pages/ClaimDocuments";
import ClaimProcessing from "./pages/ClaimProcessing";

const queryClient = new QueryClient();

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (!user) return <Navigate to="/" replace />;
  return <>{children}</>;
};

const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, isLoading } = useAuth();
  if (isLoading) return null;
  if (user) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <ClaimProvider>
            <Routes>
              <Route path="/" element={<PublicRoute><Auth /></PublicRoute>} />
              <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
              <Route path="/claim/start" element={<ProtectedRoute><ClaimStart /></ProtectedRoute>} />
              <Route path="/claim/type" element={<ProtectedRoute><ClaimType /></ProtectedRoute>} />
              <Route path="/claim/details" element={<ProtectedRoute><ClaimDetails /></ProtectedRoute>} />
              <Route path="/claim/id-verify" element={<ProtectedRoute><ClaimAadhar /></ProtectedRoute>} />
              <Route path="/claim/narrative" element={<ProtectedRoute><ClaimNarrative /></ProtectedRoute>} />
              <Route path="/claim/documents" element={<ProtectedRoute><ClaimDocuments /></ProtectedRoute>} />
              <Route path="/claim/processing" element={<ProtectedRoute><ClaimProcessing /></ProtectedRoute>} />
              <Route path="*" element={<NotFound />} />
            </Routes>
            <ChatAssistant />
          </ClaimProvider>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
