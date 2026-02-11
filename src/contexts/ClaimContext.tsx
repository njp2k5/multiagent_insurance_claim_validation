import { createContext, useContext, useEffect, useMemo, useState, ReactNode } from "react";

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

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const ensureClaimId = useMemo(
    () =>
      async () => {
        if (state.claimId) return state.claimId;
        const res = await fetch(`${API_BASE}/identity/create-claim`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({ detail: "Unable to create claim" }));
          throw new Error(err.detail || "Unable to create claim");
        }
        const data = (await res.json()) as { claim_id: string };
        setState((prev) => ({ ...prev, claimId: data.claim_id }));
        return data.claim_id;
      },
    [state.claimId]
  );

  const setClaimantType = (type: ClaimantType) => {
    setState((prev) => ({ ...prev, claimantType: type }));
  };

  const submitClaimType = async (claimType: ClaimType) => {
    const claimId = state.claimId || (await ensureClaimId());
    if (!state.claimantType) {
      throw new Error("Please select claimant type first");
    }

    const payload = {
      claim_id: claimId,
      claimant_type: state.claimantType,
      claim_type: claimType,
    };

    const res = await fetch(`${API_BASE}/identity/set-claim-info`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to set claim info" }));
      throw new Error(err.detail || "Unable to set claim info");
    }

    setState({ claimId, claimantType: state.claimantType, claimType });
  };

  const submitClaimDetails = async (
    payload: HealthClaim | VehicleClaim | PropertyClaim | LifeClaim,
    claimType: ClaimType
  ) => {
    const claimId = state.claimId || (await ensureClaimId());
    const claimantType = state.claimantType;
    if (!claimantType) throw new Error("Please select claimant type first");

    const endpointMap: Record<ClaimType, string> = {
      health: `${API_BASE}/claims/health`,
      vehicle: `${API_BASE}/claims/motor`,
      property: `${API_BASE}/claims/home`,
      life: `${API_BASE}/claims/life`,
    };

    const body = { ...payload, claim_id: claimId, claimant_type: claimantType };

    const res = await fetch(endpointMap[claimType], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to submit claim details" }));
      throw new Error(err.detail || "Unable to submit claim details");
    }

    setState((prev) => ({
      ...prev,
      claimId,
      claimantType,
      claimType,
      details: { ...prev.details, [claimType]: body as any },
    }));
  };

  const verifyAadhar = async (file: File): Promise<AadharVerification> => {
    const claimId = state.claimId || (await ensureClaimId());
    const form = new FormData();
    form.append("claim_id", claimId);
    form.append("file", file);

    const res = await fetch(`${API_BASE}/identity/extract-aadhaar`, {
      method: "POST",
      body: form,
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unable to verify Aadhaar" }));
      throw new Error(err.detail || "Unable to verify Aadhaar");
    }

    const data = (await res.json()) as AadharVerification;
    setState((prev) => ({ ...prev, aadhar: data, claimId: data.claim_id }));
    return data;
  };

  const saveNarrative = (text: string) => {
    setState((prev) => ({ ...prev, narrative: text }));
  };

  const uploadDocuments = async (files: File[]) => {
    const claimId = state.claimId || (await ensureClaimId());
    if (!files.length) {
      throw new Error("Please select at least one document");
    }

    const buildForm = () => {
      const form = new FormData();
      form.append("claim_id", claimId);
      if (files[0]) form.append("doc1", files[0]);
      if (files[1]) form.append("doc2", files[1]);
      return form;
    };

    const [validationRes, extractionRes] = await Promise.all([
      fetch(`${API_BASE}/documents/upload-and-validate`, { method: "POST", body: buildForm() }),
      fetch(`${API_BASE}/documents/extract-name-age`, { method: "POST", body: buildForm() }),
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

    setState((prev) => ({
      ...prev,
      claimId,
      documents: {
        validation,
        extraction,
        files: files.map((f) => f.name),
      },
    }));

    return { validation, extraction };
  };

  const crossValidate = async () => {
    const claimId = state.claimId || (await ensureClaimId());
    const res = await fetch(`${API_BASE}/fraud/cross-validate/${claimId}`, {
      method: "GET",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Cross-validation failed" }));
      throw new Error(err.detail || "Cross-validation failed");
    }
    setState((prev) => ({ ...prev, claimId }));
  };

  const sendReport = async (): Promise<ReportResult> => {
    const claimId = state.claimId || (await ensureClaimId());
    const url = new URL(`${API_BASE}/master/send-report`);
    url.searchParams.set("claim_id", claimId);
    const res = await fetch(url.toString(), {
      method: "GET",
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Failed to send report" }));
      throw new Error(err.detail || "Failed to send report");
    }
    const data = (await res.json()) as ReportResult;
    setState((prev) => ({ ...prev, claimId: data.claim_id ?? claimId, report: data }));
    return data;
  };

  const initChat = async (): Promise<string> => {
    const claimId = state.claimId || (await ensureClaimId());
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