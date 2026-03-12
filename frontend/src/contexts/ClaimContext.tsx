import { createContext, useCallback, useContext, useEffect, useRef, useState, ReactNode } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { terminalLog } from "@/lib/terminalLog";

type ClaimantType = "user" | "company";
type ClaimType = "health" | "vehicle" | "property" | "life";

type HealthClaim = {
  claim_id: string;
  claimant_type: "user" | "company";
  patient_name: string;
  patient_age: number;
  patient_relation: string;
  hospital_name: string;
  hospital_location: string;
  admission_date: string;
  discharge_date: string;
  diagnosis: string;
  treatment_type: string;
  treatment_description: string;
  total_bill_amount: number;
  amount_claimed: number;
  pre_existing_condition: boolean;
};

type VehicleClaim = {
  claim_id: string;
  claimant_type: "user" | "company";
  vehicle_type: string;
  vehicle_registration: string;
  vehicle_make: string;
  vehicle_model: string;
  vehicle_year: number;
  accident_date: string;
  accident_location: string;
  accident_description: string;
  damage_type: string;
  estimated_repair_cost: number;
  police_report_filed: boolean;
  third_party_involved: boolean;
};

type PropertyClaim = {
  claim_id: string;
  claimant_type: "user" | "company";
  property_type: string;
  property_address: string;
  property_value: number;
  ownership_type: string;
  incident_date: string;
  incident_type: string;
  incident_description: string;
  damage_description: string;
  estimated_loss: number;
  amount_claimed: number;
  police_report_filed: boolean;
  fire_brigade_report: boolean;
};

type LifeClaim = {
  claim_id: string;
  claimant_type: "user" | "company";
  policyholder_name: string;
  policyholder_dob: string;
  beneficiary_name: string;
  beneficiary_relation: string;
  claim_reason: string;
  event_date: string;
  event_description: string;
  cause_of_event: string;
  sum_assured: number;
  amount_claimed: number;
  death_certificate_available: boolean;
  medical_records_available: boolean;
};

type ClaimDetails = {
  health?: HealthClaim;
  vehicle?: VehicleClaim;
  property?: PropertyClaim;
  life?: LifeClaim;
};

type AadharVerification = {
  aadhaar_numbers: string[];
  verified: Record<string, boolean>;
  aadhaar_name: string;
  aadhaar_age: number;
  claim_id: string;
};

type DocumentValidation = {
  summary: string;
  agent_status: string;
  claim_id: string;
};

type DocumentExtraction = {
  document_name: string;
  document_age: number;
  claim_id: string;
};

type ReportResult = {
  message: string;
  recipient: string;
  claim_id: string;
  decision: string;
  confidence: number;
  email_sent: boolean;
};

type ChatInit = {
  session_token: string;
  claim_id: string;
  message: string;
};

type ChatMessageResponse = {
  reply: string;
  chat_history?: { user: string; assistant: string }[];
  claim_id: string;
};

interface ClaimState {
  claimId?: string;
  claimantType?: ClaimantType;
  claimType?: ClaimType;
  details?: ClaimDetails;
  aadhar?: AadharVerification;
  narrative?: string;
  documents?: {
    validation?: DocumentValidation;
    extraction?: DocumentExtraction;
    files?: string[];
  };
  report?: ReportResult;
  chat?: {
    sessionToken?: string;
    lastReply?: string;
    history?: { user: string; assistant: string }[];
  };
}

interface ClaimContextValue {
  state: ClaimState;
  startNewClaim: () => Promise<string>;
  ensureClaimId: () => Promise<string>;
  setClaimantType: (type: ClaimantType) => void;
  submitClaimType: (claimType: ClaimType) => Promise<void>;
  submitClaimDetails: (payload: HealthClaim | VehicleClaim | PropertyClaim | LifeClaim, claimType: ClaimType) => Promise<void>;
  verifyAadhar: (file: File) => Promise<AadharVerification>;
  saveNarrative: (text: string) => void;
  uploadDocuments: (files: File[]) => Promise<{ validation: DocumentValidation; extraction: DocumentExtraction }>;
  crossValidate: () => Promise<void>;
  sendReport: () => Promise<ReportResult>;
  initChat: () => Promise<string>;
  sendChatMessage: (message: string) => Promise<string>;
  fetchChatHistory: () => Promise<{ user: string; assistant: string }[]>;
}

const STORAGE_KEY = "claim_state";
const SESSION_ALIVE_KEY = "claim_session_alive";

// On every fresh page load (refresh / new tab), clear stale claim state.
// sessionStorage is cleared when the tab closes, so if the marker is missing
// it means this is a fresh session → flush the old claim data.
if (!sessionStorage.getItem(SESSION_ALIVE_KEY)) {
  localStorage.removeItem(STORAGE_KEY);
  sessionStorage.setItem(SESSION_ALIVE_KEY, "1");
}

// Module-level variable to prevent duplicate create-claim calls (survives HMR/remounts)
let createClaimInFlight: Promise<string> | null = null;

const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.toString() || "https://multiagent-insurance-claim-validation.onrender.com/api";

const ClaimContext = createContext<ClaimContextValue | null>(null);

export const ClaimProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<ClaimState>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        return JSON.parse(stored) as ClaimState;
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    return {};
  });

  const { user } = useAuth();

  // Ref to track current claimId for immediate access (avoids stale closures)
  const claimIdRef = useRef<string | undefined>(state.claimId);

  // Keep ref in sync with state
  useEffect(() => {
    claimIdRef.current = state.claimId;
  }, [state.claimId]);

  useEffect(() => {
    terminalLog("ClaimContext", "State updated — claimId:", state.claimId);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  // Sync partial state update to localStorage immediately (merges with existing)
  const syncToLocalStorage = (updates: Partial<ClaimState>) => {
    const stored = localStorage.getItem(STORAGE_KEY);
    let existingState: ClaimState = {};
    if (stored) {
      try {
        existingState = JSON.parse(stored) as ClaimState;
      } catch { /* ignore */ }
    }
    const merged = { ...existingState, ...updates };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    terminalLog("ClaimContext", "Synced to localStorage — claimId:", merged.claimId);
  };

  // Helper to get claimId reliably from ref or localStorage (sync, no stale closure issues)
  const getClaimId = (): string | undefined => {
    // Check ref first (most up-to-date)
    if (claimIdRef.current) {
      terminalLog("getClaimId", "Found in ref:", claimIdRef.current);
      return claimIdRef.current;
    }
    
    // Check localStorage directly
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored) as ClaimState;
        if (parsed.claimId) {
          terminalLog("getClaimId", "Found in localStorage:", parsed.claimId);
          claimIdRef.current = parsed.claimId;
          return parsed.claimId;
        }
      } catch { /* ignore */ }
    }
    
    terminalLog("getClaimId", "No claimId found");
    return undefined;
  };

  // Helper to get claimId or throw error
  const requireClaimId = (): string => {
    const claimId = getClaimId();
    if (!claimId) throw new Error("No claim started. Please start a new claim first.");
    return claimId;
  };

  // Helper to get claimId or auto-create one (never throws "no claim" error)
  const getOrCreateClaimId = async (): Promise<string> => {
    const existing = getClaimId();
    if (existing) return existing;
    console.warn("[getOrCreateClaimId] No claimId found anywhere, auto-creating...");
    terminalLog("getOrCreateClaimId", "No claimId found — auto-creating...");
    return startNewClaimInternal();
  };

  // Internal claim creation logic (used by both startNewClaim and getOrCreateClaimId)
  const startNewClaimInternal = async (): Promise<string> => {
    // Double-check right before creating
    const existingClaimId = getClaimId();
    if (existingClaimId) {
      terminalLog("startNewClaimInternal", "Found existing claimId:", existingClaimId);
      setState((prev) => prev.claimId === existingClaimId ? prev : { ...prev, claimId: existingClaimId });
      return existingClaimId;
    }

    // If a create-claim request is already in flight (module-level check survives HMR), wait for it
    if (createClaimInFlight) {
      terminalLog("startNewClaimInternal", "Waiting for in-flight request");
      return createClaimInFlight;
    }

    // Check sessionStorage for in-progress creation (survives HMR module reloads)
    const creatingFlag = sessionStorage.getItem("creating_claim");
    if (creatingFlag) {
      terminalLog("startNewClaimInternal", "Session flag detected, waiting...");
      await new Promise(resolve => setTimeout(resolve, 1000));
      const recheckClaimId = getClaimId();
      if (recheckClaimId) {
        terminalLog("startNewClaimInternal", "Found claimId after wait:", recheckClaimId);
        return recheckClaimId;
      }
      sessionStorage.removeItem("creating_claim");
    }

    sessionStorage.setItem("creating_claim", "true");
    terminalLog("startNewClaimInternal", "Creating new claim...");

    const createPromise = (async () => {
      try {
        const res = await fetch(`${API_BASE}/identity/create-claim`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: "Unable to create claim" }));
          throw new Error(err.detail || "Unable to create claim");
        }
        const data = (await res.json()) as { claim_id: string };
        terminalLog("startNewClaimInternal", "Created new claim:", data.claim_id);
        claimIdRef.current = data.claim_id;
        syncToLocalStorage({ claimId: data.claim_id });
        setState((prev) => ({ ...prev, claimId: data.claim_id }));
        return data.claim_id;
      } finally {
        sessionStorage.removeItem("creating_claim");
      }
    })();

    createClaimInFlight = createPromise;
    try {
      return await createPromise;
    } finally {
      createClaimInFlight = null;
    }
  };

  // Create a new claim only if one doesn't already exist (delegates to internal helper)
  const startNewClaim = useCallback(async (): Promise<string> => {
    terminalLog("startNewClaim", "Delegating to startNewClaimInternal");
    return startNewClaimInternal();
  }, []);

  // Returns existing claimId or throws error - never creates a new claim
  const ensureClaimId = useCallback(async (): Promise<string> => {
    return requireClaimId();
  }, []);

  const setClaimantType = (type: ClaimantType) => {
    terminalLog("setClaimantType", "Setting:", type);
    setState((prev) => {
      const newState = { ...prev, claimantType: type };
      // Sync immediately to localStorage
      syncToLocalStorage({ claimantType: type });
      return newState;
    });
  };

  const submitClaimType = async (claimType: ClaimType) => {
    const claimId = await getOrCreateClaimId();
    terminalLog("submitClaimType", "claim_id:", claimId, "claimType:", claimType);

    // Get claimantType from localStorage in case state is stale
    let claimantType = state.claimantType;
    if (!claimantType) {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored) as ClaimState;
          claimantType = parsed.claimantType;
        } catch { /* ignore */ }
      }
    }

    if (!claimantType) {
      throw new Error("Please select claimant type first");
    }

    const payload = {
      claim_id: claimId,
      claimant_type: claimantType,
      claim_type: claimType,
    };

    console.log("[submitClaimType] Sending payload:", JSON.stringify(payload));
    terminalLog("submitClaimType", "Sending payload — claim_id:", claimId);

    const res = await fetch(`${API_BASE}/identity/set-claim-info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to set claim info" }));
      throw new Error(err.detail || "Unable to set claim info");
    }

    terminalLog("submitClaimType", "Success — claim_id:", claimId);

    // Update ref and merge with existing state
    claimIdRef.current = claimId;
    syncToLocalStorage({ claimId, claimantType, claimType });
    setState((prev) => ({ ...prev, claimId, claimantType, claimType }));
  };

  const submitClaimDetails = async (
    payload: HealthClaim | VehicleClaim | PropertyClaim | LifeClaim,
    claimType: ClaimType
  ) => {
    const claimId = await getOrCreateClaimId();
    terminalLog("submitClaimDetails", "claim_id:", claimId, "claimType:", claimType);
    
    // Get claimantType from localStorage in case state is stale
    let claimantType = state.claimantType;
    if (!claimantType) {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        try {
          const parsed = JSON.parse(stored) as ClaimState;
          claimantType = parsed.claimantType;
        } catch { /* ignore */ }
      }
    }
    if (!claimantType) throw new Error("Please select claimant type first");

    const endpointMap: Record<ClaimType, string> = {
      health: `${API_BASE}/claims/health`,
      vehicle: `${API_BASE}/claims/motor`,
      property: `${API_BASE}/claims/home`,
      life: `${API_BASE}/claims/life`,
    };

    const body = { ...payload, claim_id: claimId, claimant_type: claimantType };

    terminalLog("submitClaimDetails", "Sending to:", endpointMap[claimType], "— claim_id:", claimId);

    const res = await fetch(endpointMap[claimType], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to submit claim details" }));
      throw new Error(err.detail || "Unable to submit claim details");
    }

    terminalLog("submitClaimDetails", "Success — claim_id:", claimId);

    const newDetails = { [claimType]: body as any };
    syncToLocalStorage({ claimId, claimantType, claimType, details: newDetails });
    setState((prev) => ({
      ...prev,
      claimId,
      claimantType,
      claimType,
      details: { ...prev.details, [claimType]: body as any },
    }));
  };

  const verifyAadhar = async (file: File): Promise<AadharVerification> => {
    const claimId = await getOrCreateClaimId();
    terminalLog("verifyAadhar", "claim_id:", claimId);
    
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`${API_BASE}/identity/extract-aadhaar?claim_id=${encodeURIComponent(claimId)}`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to verify Aadhaar" }));
      throw new Error(err.detail || "Unable to verify Aadhaar");
    }

    const data = (await res.json()) as AadharVerification;
    const resolvedClaimId = data.claim_id ?? claimId;
    terminalLog("verifyAadhar", "Success — response claim_id:", data.claim_id, "→ using:", resolvedClaimId);
    
    syncToLocalStorage({ aadhar: data, claimId: resolvedClaimId });
    setState((prev) => ({ ...prev, aadhar: data, claimId: resolvedClaimId }));
    return data;
  };

  const saveNarrative = (text: string) => {
    terminalLog("saveNarrative", "Saving narrative — claimId:", getClaimId());
    syncToLocalStorage({ narrative: text });
    setState((prev) => ({ ...prev, narrative: text }));
  };

  const uploadDocuments = async (files: File[]) => {
    const claimId = await getOrCreateClaimId();
    terminalLog("uploadDocuments", "claim_id:", claimId);
    
    if (!files.length) {
      throw new Error("Please select at least one document");
    }

    const buildForm = () => {
      const form = new FormData();
      if (files[0]) form.append("doc1", files[0]);
      if (files[1]) form.append("doc2", files[1]);
      return form;
    };

    const queryParam = `?claim_id=${encodeURIComponent(claimId)}`;

    const [validationRes, extractionRes] = await Promise.all([
      fetch(`${API_BASE}/documents/upload-and-validate${queryParam}`, { method: "POST", body: buildForm() }),
      fetch(`${API_BASE}/documents/extract-name-age${queryParam}`, { method: "POST", body: buildForm() }),
    ]);

    if (!validationRes.ok) {
      const err = await validationRes.json().catch(() => ({ detail: "Document validation failed" }));
      throw new Error(err.detail || "Document validation failed");
    }
    if (!extractionRes.ok) {
      const err = await extractionRes.json().catch(() => ({ detail: "Document extraction failed" }));
      throw new Error(err.detail || "Document extraction failed");
    }

    const validation = (await validationRes.json()) as DocumentValidation;
    const extraction = (await extractionRes.json()) as DocumentExtraction;
    
    terminalLog("uploadDocuments", "Success — claim_id:", claimId);

    const docs = {
      validation,
      extraction,
      files: files.map((f) => f.name),
    };
    syncToLocalStorage({ claimId, documents: docs });
    setState((prev) => ({
      ...prev,
      claimId,
      documents: docs,
    }));

    return { validation, extraction };
  };

  const crossValidate = async () => {
    const claimId = await getOrCreateClaimId();
    terminalLog("crossValidate", "claim_id:", claimId);

    // Step 7: Call policy check to populate backend state before cross-validation
    try {
      terminalLog("crossValidate", "Calling policy/check — claim_id:", claimId);
      const policyRes = await fetch(`${API_BASE}/policy/check?claim_id=${claimId}`, {
        method: "GET",
      });
      if (!policyRes.ok) {
        const policyErr = await policyRes.text().catch(() => "unknown");
        terminalLog("crossValidate", "Policy check FAILED — status:", policyRes.status, "body:", policyErr);
      } else {
        const policyData = await policyRes.json().catch(() => null);
        terminalLog("crossValidate", "Policy check succeeded — response:", JSON.stringify(policyData));
      }
    } catch (err) {
      terminalLog("crossValidate", "Policy check error (non-critical):", String(err));
    }

    // Step 8: Cross-validate
    terminalLog("crossValidate", "Calling fraud/cross-validate — claim_id:", claimId);
    const res = await fetch(`${API_BASE}/fraud/cross-validate/${claimId}`, {
      method: "GET",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Cross-validation failed" }));
      throw new Error(err.detail || "Cross-validation failed");
    }
    const cvResult = await res.json();
    terminalLog("crossValidate", "Response:", JSON.stringify(cvResult));
    terminalLog("crossValidate", "Status:", cvResult.status, "| confidence:", cvResult.confidence, "| name_match:", cvResult.name_match, "| age_match:", cvResult.age_match);
    terminalLog("crossValidate", "Success — claim_id:", claimId);
    setState((prev) => ({ ...prev, claimId }));
  };

  const sendReport = async (): Promise<ReportResult> => {
    const claimId = await getOrCreateClaimId();
    terminalLog("sendReport", "claim_id:", claimId);
    
    if (!user?.username || !user?.password) {
      throw new Error("You must be signed in to send the report");
    }
    const credentials = btoa(`${user.username}:${user.password}`);
    const url = new URL(`${API_BASE}/master/send-report`);
    url.searchParams.set("claim_id", claimId);
    url.searchParams.set("user_email", user.username);
    
    terminalLog("sendReport", "Sending to:", url.toString());
    
    const res = await fetch(url.toString(), {
      method: "GET",
      headers: {
        Authorization: `Basic ${credentials}`,
      },
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to send report" }));
      throw new Error(err.detail || "Failed to send report");
    }
    const data = (await res.json()) as ReportResult;
    terminalLog("sendReport", "Full response:", JSON.stringify(data));
    terminalLog("sendReport", "Success — decision:", data.decision, "confidence:", data.confidence, "claim_id:", claimId);
    
    syncToLocalStorage({ claimId: data.claim_id ?? claimId, report: data });
    setState((prev) => ({ ...prev, claimId: data.claim_id ?? claimId, report: data }));
    return data;
  };

  const initChat = async (): Promise<string> => {
    const claimId = await getOrCreateClaimId();
    const res = await fetch(`${API_BASE}/chat/init`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ claim_id: claimId }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to start chat" }));
      throw new Error(err.detail || "Unable to start chat");
    }
    const data = (await res.json()) as ChatInit;
    setState((prev) => ({
      ...prev,
      claimId: data.claim_id || claimId,
      chat: { sessionToken: data.session_token, lastReply: data.message, history: [] },
    }));
    return data.session_token;
  };

  const requireSession = async () => {
    if (state.chat?.sessionToken) return state.chat.sessionToken;
    return initChat();
  };

  const sendChatMessage = async (message: string): Promise<string> => {
    const sessionToken = await requireSession();
    const res = await fetch(`${API_BASE}/chat/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_token: sessionToken }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Chat send failed" }));
      throw new Error(err.detail || "Chat send failed");
    }
    const data = (await res.json()) as ChatMessageResponse;
    setState((prev) => ({
      ...prev,
      chat: {
        sessionToken,
        lastReply: data.reply,
        history: data.chat_history || prev.chat?.history || [],
      },
    }));
    return data.reply;
  };

  const fetchChatHistory = async (): Promise<{ user: string; assistant: string }[]> => {
    const sessionToken = await requireSession();
    const res = await fetch(`${API_BASE}/chat/history/${sessionToken}`, {
      method: "GET",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to fetch history" }));
      throw new Error(err.detail || "Unable to fetch history");
    }
    const data = (await res.json()) as { chat_history: { user: string; assistant: string }[] };
    setState((prev) => ({
      ...prev,
      chat: {
        sessionToken,
        lastReply: prev.chat?.lastReply,
        history: data.chat_history,
      },
    }));
    return data.chat_history;
  };

  return (
    <ClaimContext.Provider
      value={{
        state,
        startNewClaim,
        ensureClaimId,
        setClaimantType,
        submitClaimType,
        submitClaimDetails,
        verifyAadhar,
        saveNarrative,
        uploadDocuments,
        crossValidate,
        sendReport,
        initChat,
        sendChatMessage,
        fetchChatHistory,
      }}
    >
      {children}
    </ClaimContext.Provider>
  );
};

export const useClaim = () => {
  const ctx = useContext(ClaimContext);
  if (!ctx) throw new Error("useClaim must be used within ClaimProvider");
  return ctx;
};