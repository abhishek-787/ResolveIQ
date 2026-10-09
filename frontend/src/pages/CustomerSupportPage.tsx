import {
  useEffect,
  useState,
} from "react";

import type {
  SyntheticEvent,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  askSupport,
  askSupportWithImage,
  getConversationHistory,
} from "../api/client";

import type {
  SupportSource,
} from "../types/api";


interface ChatMessage {
  id: number;
  role: "customer" | "agent";
  content: string;
  sources?: SupportSource[];
  imageUrl?: string;
}


const CONVERSATION_STORAGE_KEY =
  "resolveiq_conversation_id";


const initialMessage: ChatMessage = {
  id: 1,
  role: "agent",
  content:
    "Hi! I'm ResolveIQ. How can I help with your ShopEase order today?",
};


function CustomerSupportPage() {
  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>([
    initialMessage,
  ]);

  const [
    query,
    setQuery,
  ] = useState("");

  const [
    conversationId,
    setConversationId,
  ] = useState<number | null>(
    null
  );

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(
    null
  );

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    restoringConversation,
    setRestoringConversation,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null
  );


  useEffect(
    () => {

      async function restoreConversation() {
        const storedId =
          localStorage.getItem(
            CONVERSATION_STORAGE_KEY
          );

        if (!storedId) {
          setRestoringConversation(
            false
          );

          return;
        }

        const parsedId =
          Number(
            storedId
          );

        if (
          !Number.isInteger(
            parsedId
          )
        ) {
          localStorage.removeItem(
            CONVERSATION_STORAGE_KEY
          );

          setRestoringConversation(
            false
          );

          return;
        }

        try {
          const history =
            await getConversationHistory(
              parsedId
            );

          const restoredMessages:
            ChatMessage[] =
            history.messages.map(
              (
                message,
                index,
              ) => {

                const sender =
                  String(
                    message.sender
                  ).toLowerCase();

                return {
                  id:
                    index + 1,

                  role:
                    sender.includes(
                      "customer"
                    )
                      ? "customer"
                      : "agent",

                  content:
                    message.content,
                };
              }
            );

          setConversationId(
            history.conversation_id
          );

          if (
            restoredMessages.length
            > 0
          ) {
            setMessages(
              restoredMessages
            );
          }

        } catch {
          localStorage.removeItem(
            CONVERSATION_STORAGE_KEY
          );

          setConversationId(
            null
          );

          setMessages([
            initialMessage,
          ]);

        } finally {
          setRestoringConversation(
            false
          );
        }
      }


      restoreConversation();

    },
    []
  );


  async function handleSubmit(
    event:
      SyntheticEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const trimmedQuery =
      query.trim();

    if (
      !trimmedQuery
      || loading
      || restoringConversation
    ) {
      return;
    }

    const imageUrl =
  selectedFile
    ? URL.createObjectURL(
        selectedFile
      )
    : undefined;


const customerMessage:
  ChatMessage = {
    id: Date.now(),

    role:
      "customer",

    content:
      trimmedQuery,

    imageUrl:
      imageUrl,
  };

    setMessages(
      (current) => [
        ...current,
        customerMessage,
      ]
    );

    setQuery("");
    setError(null);
    setLoading(true);

    try {
      const response =
        selectedFile
          ? await askSupportWithImage(
              trimmedQuery,
              selectedFile,
              conversationId,
            )
          : await askSupport(
              trimmedQuery,
              conversationId,
            );

      setConversationId(
        response.conversation_id
      );

      localStorage.setItem(
        CONVERSATION_STORAGE_KEY,
        String(
          response.conversation_id
        )
      );

      const agentMessage:
        ChatMessage = {
          id:
            Date.now() + 1,

          role:
            "agent",

          content:
            response.answer,

          sources:
            response.sources,
        };

      setMessages(
        (current) => [
          ...current,
          agentMessage,
        ]
      );

      setSelectedFile(
        null
      );

    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Something went wrong.";

      setError(
        message
      );

    } finally {
      setLoading(
        false
      );
    }
  }


  function handleNewChat() {
    localStorage.removeItem(
      CONVERSATION_STORAGE_KEY
    );

    setConversationId(
      null
    );

    setSelectedFile(
      null
    );

    setQuery("");

    setError(
      null
    );

    setMessages([
      {
        id: Date.now(),
        role: "agent",
        content:
          "New conversation started. How can I help?",
      },
    ]);
  }


  return (
    <div className="app-shell">

      <header className="top-bar">

        <div>
          <h1>
            ResolveIQ
          </h1>

          <p>
            ShopEase AI Support
          </p>
        </div>

        <div className="top-actions">

          <button
            type="button"
            className="secondary-button"
            onClick={
              handleNewChat
            }
          >
            New chat
          </button>

          <Link
            to="/admin"
            className="admin-link"
          >
            Admin
          </Link>

        </div>

      </header>


      <main className="chat-card">

        <section className="chat-header">

          <div>
            <h2>
              Customer Support
            </h2>

            <p>
              Ask about orders,
              returns, refunds,
              damaged products,
              delivery or product
              issues.
            </p>
          </div>

          <span className="status-badge">
            Online
          </span>

        </section>


        <section className="messages">

          {
            restoringConversation
            ? (
                <div
                  className="message-row agent"
                >
                  <div
                    className="message-bubble loading-message"
                  >
                    Loading previous
                    conversation...
                  </div>
                </div>
              )

            : messages.map(
                (message) => (

                  <div
                    key={
                      message.id
                    }
                    className={
                      `message-row ${
                        message.role
                      }`
                    }
                  >

                    <div
                      className="message-bubble"
                    >

                      <div
                        className="message-label"
                      >
                        {
                          message.role
                          === "customer"
                            ? "You"
                            : "ResolveIQ"
                        }
                      </div>

                      {
                        message.imageUrl
                        && (
                          <img
                            src={
                              message.imageUrl
                            }
                            alt="Customer attachment"
                            className="chat-image"
                          />
                        )
                      }

                      <p>
                        {
                          message.content
                        }
                      </p>


                      {
                        message.sources
                        && message
                          .sources
                          .length > 0
                        && (

                          <div
                            className="source-list"
                          >

                            <span
                              className="source-title"
                            >
                              Sources
                            </span>

                            {
                              message.sources.map(
                                (
                                  source
                                ) => (

                                  <div
                                    key={
                                      source
                                        .citation_id
                                    }
                                    className="source-item"
                                  >

                                    <strong>
                                      [
                                      {
                                        source
                                          .citation_id
                                      }
                                      ]
                                    </strong>

                                    <span>
                                      {
                                        source
                                          .document_code
                                      }

                                      {" · "}

                                      {
                                        source
                                          .section_title
                                      }
                                    </span>

                                  </div>

                                )
                              )
                            }

                          </div>

                        )
                      }

                    </div>

                  </div>

                )
              )
          }


          {
            loading
            && (

              <div
                className="message-row agent"
              >

                <div
                  className="
                    message-bubble
                    loading-message
                  "
                >
                  ResolveIQ is checking
                  your request...
                </div>

              </div>

            )
          }

        </section>


        {
          selectedFile
          && (

            <div
              className="selected-file"
            >

              <span>
                Attached:
                {" "}
                {
                  selectedFile.name
                }
              </span>

              <button
                type="button"
                onClick={
                  () =>
                    setSelectedFile(
                      null
                    )
                }
              >
                Remove
              </button>

            </div>

          )
        }


        {
          error
          && (
            <div
              className="error-box"
            >
              {error}
            </div>
          )
        }


        <form
          className="composer"
          onSubmit={
            handleSubmit
          }
        >

          <label
            className="attach-button"
          >
            Attach

            <input
              type="file"
              accept="
                image/jpeg,
                image/png,
                image/webp
              "
              hidden
              disabled={
                loading
                || restoringConversation
              }
              onChange={
                (event) => {

                  const file =
                    event
                      .target
                      .files?.[0];

                  if (file) {
                    setSelectedFile(
                      file
                    );
                  }
                }
              }
            />

          </label>


          <input
            className="message-input"
            type="text"
            value={query}
            placeholder={
              selectedFile
                ? "Ask about this image..."
                : "Ask about your ShopEase order..."
            }
            disabled={
              loading
              || restoringConversation
            }
            onChange={
              (event) =>
                setQuery(
                  event.target.value
                )
            }
          />


          <button
            className="send-button"
            type="submit"
            disabled={
              loading
              || restoringConversation
              || !query.trim()
            }
          >
            {
              loading
                ? "Sending..."
                : "Send"
            }
          </button>

        </form>

      </main>

    </div>
  );
}


export default CustomerSupportPage;