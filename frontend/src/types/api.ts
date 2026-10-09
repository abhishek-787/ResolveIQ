export interface SupportSource {
  citation_id: string;
  document_code: string;
  document_type: string;
  version_label?: string | null;
  section_title: string;
  source_filename: string;
}

export interface SupportResponse {
  conversation_id: number;
  answer: string;
  sources: SupportSource[];
}

export interface ApprovalRequest {
  approval_code: string;
  conversation_id: number | null;
  order_number: string | null;
  action: string;
  status: string;
  reason: string;
  requested_at: string;
  reviewed_at: string | null;
  reviewed_by: string | null;
  review_note: string | null;
}

export interface ActionExecution {
  execution_code: string;
  approval_request_id: number;
  conversation_id: number | null;
  order_number: string | null;
  action: string;
  status: string;
  result_reference: string | null;
  result_message: string | null;
  error_message: string | null;
  executed_by: string;
  created_at: string;
  executed_at: string | null;
}

export interface ApproveAndExecuteResponse {
  approval_code: string;
  approval_status: string;
  execution: ActionExecution;
}

export interface AgentRun {
  run_code: string;
  run_type: string;
  case_id: string | null;
  conversation_id: number | null;
  user_query: string;
  route: string | null;
  selected_tools: string[];
  knowledge_sufficient: boolean | null;
  resolution_action: string | null;
  guardrail_status: string | null;
  citation_ids: string[];
  latency_ms: number;
  success: boolean;
  error_message: string | null;
  final_answer_preview: string | null;
  created_at: string;
}

export interface ConversationMessage {
  sender: string;
  content: string;
  created_at?: string;
}

export interface ConversationHistoryResponse {
  conversation_id: number;
  message_count: number;
  messages: ConversationMessage[];
}