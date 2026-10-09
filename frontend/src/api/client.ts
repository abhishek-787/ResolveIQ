import type {
  AgentRun,
  ApprovalRequest,
  ApproveAndExecuteResponse,
  ConversationHistoryResponse,
  SupportResponse,
} from "../types/api";



const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";


async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    options,
  );

  if (!response.ok) {
    let message = "Request failed.";

    try {
      const data = await response.json();

      message =
        data.detail ??
        data.message ??
        message;
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function askSupport(
  query: string,
  conversationId?: number | null,
): Promise<SupportResponse> {
  return apiRequest<SupportResponse>(
    "/support/ask",
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        query,
        conversation_id:
          conversationId ?? null,
      }),
    },
  );
}

export async function askSupportWithImage(
  query: string,
  file: File,
  conversationId?: number | null,
): Promise<SupportResponse> {
  const formData = new FormData();

  formData.append(
    "query",
    query,
  );

  formData.append(
    "file",
    file,
  );

  if (conversationId) {
    formData.append(
      "conversation_id",
      String(
        conversationId,
      ),
    );
  }

  return apiRequest<SupportResponse>(
    "/support/ask-with-image",
    {
      method: "POST",
      body: formData,
    },
  );
}

export async function getPendingApprovals(
): Promise<ApprovalRequest[]> {
  return apiRequest<
    ApprovalRequest[]
  >(
    "/admin/approvals",
  );
}


export async function approveAndExecute(
  approvalCode: string,
  reviewedBy: string,
  note?: string,
): Promise<ApproveAndExecuteResponse> {
  return apiRequest<
    ApproveAndExecuteResponse
  >(
    `/admin/approvals/${approvalCode}/approve-and-execute`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        reviewed_by:
          reviewedBy,

        note:
          note ?? null,
      }),
    },
  );
}


export async function rejectApproval(
  approvalCode: string,
  reviewedBy: string,
  note?: string,
): Promise<ApprovalRequest> {
  return apiRequest<
    ApprovalRequest
  >(
    `/admin/approvals/${approvalCode}/reject`,
    {
      method: "POST",

      headers: {
        "Content-Type":
          "application/json",
      },

      body: JSON.stringify({
        reviewed_by:
          reviewedBy,

        note:
          note ?? null,
      }),
    },
  );
}


export async function getRecentRuns(
  limit = 20,
): Promise<AgentRun[]> {
  return apiRequest<
    AgentRun[]
  >(
    `/admin/observability/runs?limit=${limit}`,
  );
}

export async function getConversationHistory(
  conversationId: number,
): Promise<ConversationHistoryResponse> {
  return apiRequest<
    ConversationHistoryResponse
  >(
    `/support/conversations/${conversationId}`,
  );
}

export async function ingestKnowledgeDocument(
  file: File,
  documentType: string,
  documentKey: string,
  versionLabel: string,
): Promise<unknown> {
  const formData = new FormData();

  formData.append(
    "document_type",
    documentType,
  );

  formData.append(
    "document_key",
    documentKey,
  );

  formData.append(
    "version_label",
    versionLabel,
  );

  formData.append(
    "file",
    file,
  );

  return apiRequest<unknown>(
    "/admin/documents/ingest",
    {
      method: "POST",
      body: formData,
    },
  );
}