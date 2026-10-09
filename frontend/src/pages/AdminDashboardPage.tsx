import {
  useEffect,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  approveAndExecute,
  getPendingApprovals,
  getRecentRuns,
  ingestKnowledgeDocument,
  rejectApproval,
} from "../api/client";

import type {
  AgentRun,
  ApprovalRequest,
} from "../types/api";


function formatAction(
  action: string,
) {
  return action
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase(),
    );
}


function formatLatency(
  latencyMs: number,
) {
  if (latencyMs < 1000) {
    return `${Math.round(
      latencyMs
    )} ms`;
  }

  return `${(
    latencyMs / 1000
  ).toFixed(2)} s`;
}


function AdminDashboardPage() {
  const [
    approvals,
    setApprovals,
  ] = useState<
    ApprovalRequest[]
  >([]);

  const [
    runs,
    setRuns,
  ] = useState<
    AgentRun[]
  >([]);

  const [
    selectedKnowledgeFile,
    setSelectedKnowledgeFile,
  ] = useState<File | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    actionLoading,
    setActionLoading,
  ] = useState<
    string | null
  >(null);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const [
    successMessage,
    setSuccessMessage,
  ] = useState<
    string | null
  >(null);

  const [
  documentType,
  setDocumentType,
] = useState(
  "returns_refunds"
);

  const [
    documentKey,
    setDocumentKey,
  ] = useState("");

  const [
    versionLabel,
    setVersionLabel,
  ] = useState("");

  const [
    knowledgeUploading,
    setKnowledgeUploading,
  ] = useState(false);

  async function loadDashboard() {
    setError(
      null
    );

    try {
      const [
        approvalData,
        runData,
      ] = await Promise.all([
        getPendingApprovals(),
        getRecentRuns(20),
      ]);

      setApprovals(
        approvalData
      );

      setRuns(
        runData
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : (
              "Unable to load "
              + "admin dashboard."
            )
      );

    } finally {
      setLoading(
        false
      );
    }
  }


  useEffect(
    () => {
      loadDashboard();
    },
    []
  );


  async function handleApproveAndExecute(
    approval:
      ApprovalRequest,
  ) {
    const confirmed =
      window.confirm(
        `Approve and execute ${formatAction(
          approval.action
        )} for ${
          approval.order_number
          ?? "this case"
        }?`
      );

    if (!confirmed) {
      return;
    }

    setActionLoading(
      approval.approval_code
    );

    setError(
      null
    );

    setSuccessMessage(
      null
    );

    try {
      const result =
        await approveAndExecute(
          approval.approval_code,
          "support_manager_01",
          (
            "Reviewed and approved "
            + "from ResolveIQ admin."
          ),
        );

      setSuccessMessage(
        `${
          formatAction(
            result.execution.action
          )
        } completed successfully. `
        + `Reference: ${
          result.execution
            .result_reference
          ?? "N/A"
        }`
      );

      await loadDashboard();

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : (
              "Approval execution "
              + "failed."
            )
      );

    } finally {
      setActionLoading(
        null
      );
    }
  }


  async function handleReject(
    approval:
      ApprovalRequest,
  ) {
    const note =
      window.prompt(
        "Reason for rejection:",
        (
          "Request requires "
          + "further review."
        ),
      );

    if (note === null) {
      return;
    }

    setActionLoading(
      approval.approval_code
    );

    setError(
      null
    );

    setSuccessMessage(
      null
    );

    try {
      await rejectApproval(
        approval.approval_code,
        "support_manager_01",
        note,
      );

      setSuccessMessage(
        `${approval.approval_code} rejected.`
      );

      await loadDashboard();

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : (
              "Unable to reject "
              + "approval."
            )
      );

    } finally {
      setActionLoading(
        null
      );
    }
  }


 async function handleKnowledgeUpload() {
  if (
    !selectedKnowledgeFile
    || !documentType
    || !documentKey.trim()
    || !versionLabel.trim()
  ) {
    setError(
      "Please select a file and complete all document fields."
    );

    return;
  }

  setKnowledgeUploading(
    true
  );

  setError(
    null
  );

  setSuccessMessage(
    null
  );

  try {
    await ingestKnowledgeDocument(
      selectedKnowledgeFile,
      documentType,
      documentKey.trim(),
      versionLabel.trim(),
    );

    setSuccessMessage(
      "Document successfully extracted, chunked, embedded and indexed."
    );

    setSelectedKnowledgeFile(
      null
    );

    setDocumentKey(
      ""
    );

    setVersionLabel(
      ""
    );

  } catch (err) {
    setError(
      err instanceof Error
        ? err.message
        : "Knowledge ingestion failed."
    );

  } finally {
    setKnowledgeUploading(
      false
    );
  }
}


  return (
    <div className="admin-shell">

      <header className="admin-top-bar">

        <div>
          <h1>
            ResolveIQ Admin
          </h1>

          <p>
            ShopEase Support
            Operations
          </p>
        </div>

        <div
          className="admin-top-actions"
        >
          <button
            type="button"
            className="secondary-button"
            onClick={
              loadDashboard
            }
          >
            Refresh
          </button>

          <Link
            to="/"
            className="admin-link"
          >
            Customer Support
          </Link>
        </div>

      </header>


      {
        error
        && (
          <div className="error-box admin-message">
            {error}
          </div>
        )
      }


      {
        successMessage
        && (
          <div className="success-box">
            {successMessage}
          </div>
        )
      }


      <main className="admin-content">

        {/* ----------------------- */}
        {/* KNOWLEDGE BASE          */}
        {/* ----------------------- */}

        <section className="admin-section">

          <div className="section-heading">

            <div>
              <h2>
                Knowledge Base
              </h2>

              <p>
                Upload ShopEase
                policies, FAQs or
                product manuals.
              </p>
            </div>

            <span
              className="section-tag"
            >
              PDF / TXT
            </span>

          </div>


          <div className="knowledge-form">

  <div className="knowledge-field">

    <label>
      Document Type
    </label>

    <select
      value={
        documentType
      }
      onChange={
        (event) =>
          setDocumentType(
            event.target.value
          )
      }
      disabled={
        knowledgeUploading
      }
    >
      <option value="returns_refunds">
        Returns & Refunds
      </option>

      <option value="damaged_defective">
        Damaged / Defective
      </option>

      <option value="shipping_delivery">
        Shipping / Delivery
      </option>

      <option value="warranty">
        Warranty
      </option>

      <option value="payment_refund">
        Payment / Refund
      </option>

      <option value="product_manual">
        Product Manual
      </option>

      <option value="faq">
        FAQ
      </option>

      <option value="other">
        Other
      </option>
    </select>

  </div>


  <div className="knowledge-field">

    <label>
      Document Key
    </label>

    <input
      type="text"
      value={
        documentKey
      }
      placeholder="returns-refunds-policy"
      disabled={
        knowledgeUploading
      }
      onChange={
        (event) =>
          setDocumentKey(
            event.target.value
          )
      }
    />

  </div>


  <div className="knowledge-field">

    <label>
      Version
    </label>

    <input
      type="text"
      value={
        versionLabel
      }
      placeholder="v3.0"
      disabled={
        knowledgeUploading
      }
      onChange={
        (event) =>
          setVersionLabel(
            event.target.value
          )
      }
    />

  </div>


  <div className="knowledge-file-row">

    <label
      className="knowledge-file-picker"
    >
      Choose File

      <input
        type="file"
        accept=".pdf,.txt,application/pdf,text/plain"
        hidden
        disabled={
          knowledgeUploading
        }
        onChange={
          (event) => {

            const file =
              event.target
                .files?.[0];

            if (file) {
              setSelectedKnowledgeFile(
                file
              );
            }
          }
        }
      />

    </label>


    <div
      className="knowledge-file-name"
    >
      {
        selectedKnowledgeFile
          ? selectedKnowledgeFile.name
          : "No file selected"
      }
    </div>


    <button
      type="button"
      className="primary-button"
      disabled={
        knowledgeUploading
        || !selectedKnowledgeFile
        || !documentKey.trim()
        || !versionLabel.trim()
      }
      onClick={
        handleKnowledgeUpload
      }
    >
      {
        knowledgeUploading
          ? "Ingesting..."
          : "Ingest Document"
      }
    </button>

  </div>

</div>


          <p
            className="section-note"
          >
            Uploaded documents are
            processed through
            ResolveIQ's extraction,
            chunking, embedding and
            pgvector indexing
            pipeline.
          </p>

        </section>


        {/* ----------------------- */}
        {/* APPROVALS               */}
        {/* ----------------------- */}

        <section className="admin-section">

          <div className="section-heading">

            <div>
              <h2>
                Pending Approvals
              </h2>

              <p>
                Sensitive actions
                waiting for human
                review.
              </p>
            </div>

            <span
              className="section-count"
            >
              {approvals.length}
            </span>

          </div>


          {
            loading
            ? (
                <p
                  className="empty-state"
                >
                  Loading approvals...
                </p>
              )

            : approvals.length === 0
            ? (
                <p
                  className="empty-state"
                >
                  No pending
                  approvals.
                </p>
              )

            : (
                <div
                  className="approval-list"
                >

                  {
                    approvals.map(
                      (approval) => (

                        <article
                          key={
                            approval
                              .approval_code
                          }
                          className="approval-card"
                        >

                          <div
                            className="approval-main"
                          >

                            <div
                              className="approval-code"
                            >
                              {
                                approval
                                  .approval_code
                              }
                            </div>

                            <h3>
                              {
                                formatAction(
                                  approval.action
                                )
                              }
                            </h3>

                            <div
                              className="approval-meta"
                            >
                              <span>
                                Order:
                                {" "}
                                {
                                  approval
                                    .order_number
                                  ?? "N/A"
                                }
                              </span>

                              <span>
                                Conversation:
                                {" "}
                                {
                                  approval
                                    .conversation_id
                                  ?? "N/A"
                                }
                              </span>
                            </div>

                            <p>
                              {
                                approval.reason
                              }
                            </p>

                          </div>


                          <div
                            className="approval-actions"
                          >

                            <button
                              type="button"
                              className="reject-button"
                              disabled={
                                actionLoading
                                === approval
                                  .approval_code
                              }
                              onClick={
                                () =>
                                  handleReject(
                                    approval
                                  )
                              }
                            >
                              Reject
                            </button>

                            <button
                              type="button"
                              className="primary-button"
                              disabled={
                                actionLoading
                                === approval
                                  .approval_code
                              }
                              onClick={
                                () =>
                                  handleApproveAndExecute(
                                    approval
                                  )
                              }
                            >
                              {
                                actionLoading
                                === approval
                                  .approval_code
                                  ? "Processing..."
                                  : (
                                      "Approve "
                                      + "& Execute"
                                    )
                              }
                            </button>

                          </div>

                        </article>

                      )
                    )
                  }

                </div>
              )
          }

        </section>


        {/* ----------------------- */}
        {/* OBSERVABILITY           */}
        {/* ----------------------- */}

        <section className="admin-section">

          <div className="section-heading">

            <div>
              <h2>
                Agent Observability
              </h2>

              <p>
                Recent ResolveIQ
                support and
                evaluation runs.
              </p>
            </div>

            <span
              className="section-count"
            >
              {runs.length}
            </span>

          </div>


          {
            loading
            ? (
                <p
                  className="empty-state"
                >
                  Loading agent runs...
                </p>
              )

            : runs.length === 0
            ? (
                <p
                  className="empty-state"
                >
                  No agent runs
                  available.
                </p>
              )

            : (
                <div
                  className="runs-list"
                >

                  {
                    runs.map(
                      (run) => (

                        <article
                          key={
                            run.run_code
                          }
                          className="run-card"
                        >

                          <div
                            className="run-top"
                          >

                            <div>

                              <strong>
                                {
                                  run.run_code
                                }
                              </strong>

                              <span
                                className="run-type"
                              >
                                {
                                  run.run_type
                                }
                              </span>

                            </div>


                            <span
                              className={
                                run.success
                                  ? (
                                      "run-status "
                                      + "success"
                                    )
                                  : (
                                      "run-status "
                                      + "failed"
                                    )
                              }
                            >
                              {
                                run.success
                                  ? "Success"
                                  : "Failed"
                              }
                            </span>

                          </div>


                          <p
                            className="run-query"
                          >
                            {
                              run.user_query
                            }
                          </p>


                          <div
                            className="run-details"
                          >

                            <span>
                              Route:
                              {" "}
                              {
                                run.route
                                ?? "N/A"
                              }
                            </span>

                            <span>
                              Resolution:
                              {" "}
                              {
                                run
                                  .resolution_action
                                ? formatAction(
                                    run
                                      .resolution_action
                                  )
                                : "N/A"
                              }
                            </span>

                            <span>
                              Guardrail:
                              {" "}
                              {
                                run
                                  .guardrail_status
                                ?? "N/A"
                              }
                            </span>

                            <span>
                              Latency:
                              {" "}
                              {
                                formatLatency(
                                  run.latency_ms
                                )
                              }
                            </span>

                          </div>


                          {
                            run.selected_tools
                              .length > 0
                            && (

                              <div
                                className="run-tools"
                              >
                                <strong>
                                  Tools:
                                </strong>

                                {
                                  run
                                    .selected_tools
                                    .join(
                                      ", "
                                    )
                                }
                              </div>

                            )
                          }


                          {
                            run.error_message
                            && (

                              <div
                                className="run-error"
                              >
                                {
                                  run
                                    .error_message
                                }
                              </div>

                            )
                          }

                        </article>

                      )
                    )
                  }

                </div>
              )
          }

        </section>

      </main>

    </div>
  );
}


export default AdminDashboardPage;