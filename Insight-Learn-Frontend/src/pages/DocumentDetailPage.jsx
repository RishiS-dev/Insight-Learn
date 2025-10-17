import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { listDocuments, deleteDocument } from "../api/documents";
import { getLatestSummary, generateSummary } from "../api/summaries";
import { listFlashcards, generateFlashcards } from "../api/flashcards";
import { getRelatedVideos } from "../api/videos";
import { useEffect, useState } from "react";
import { chatWithDoc, clearChatHistory, getChatHistory } from "../api/chat";
import { Trash2, RefreshCw } from "lucide-react";

export default function DocumentDetailPage() {
  const { docId } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();

  const { data: docs } = useQuery({ queryKey: ["documents"], queryFn: listDocuments });
  const doc = docs?.documents?.find((d) => String(d.id) === docId);

  const { data: latestSummary, refetch: refetchLatestSummary } = useQuery({
    queryKey: ["summary", docId],
    queryFn: () => getLatestSummary(docId),
    enabled: !!docId,
  });

  const { data: flashcardData, refetch: refetchFlashcards, isLoading: fcLoadingFetch } = useQuery({
    queryKey: ["flashcards", docId],
    queryFn: () => listFlashcards(docId),
    enabled: !!docId,
  });

  const { data: chatHistoryData } = useQuery({
    queryKey: ["chatHistory", docId],
    queryFn: () => getChatHistory(docId, 50),
    enabled: !!docId,
  });

  const {
    data: videosData,
    refetch: refetchVideos,
    isFetching: videosLoading,
  } = useQuery({
    queryKey: ["videos", docId],
    queryFn: () => getRelatedVideos(docId, { limit: 6, force: false }),
    enabled: !!docId,
    staleTime: 1000 * 60 * 60, // 1h
  });

  const [summGenLoading, setSummGenLoading] = useState(false);
  const [fcGenLoading, setFcGenLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    if (chatHistoryData?.messages && Array.isArray(chatHistoryData.messages)) {
      setChatMessages(chatHistoryData.messages);
    } else {
      setChatMessages([]);
    }
    setChatInput("");
    setChatLoading(false);
  }, [docId, chatHistoryData]);

  async function doGenerateSummary(force = false) {
    setSummGenLoading(true);
    try {
      await generateSummary(docId, { force });
      await refetchLatestSummary();
      await refetchVideos(); // keep videos aligned with summary
    } finally {
      setSummGenLoading(false);
    }
  }

  async function doGenerateFlashcards(force = false) {
    setFcGenLoading(true);
    try {
      await generateFlashcards(docId, 6, { force });
      await refetchFlashcards();
    } finally {
      setFcGenLoading(false);
    }
  }

  async function sendChat() {
    if (!chatInput.trim()) return;
    const q = chatInput.trim();
    setChatMessages((m) => [...m, { role: "user", text: q }]);
    setChatInput("");
    setChatLoading(true);
    try {
      const res = await chatWithDoc(docId, q);
      setChatMessages((m) => [...m, { role: "assistant", text: res.answer }]);
    } catch {
      setChatMessages((m) => [...m, { role: "assistant", text: "Error answering." }]);
    } finally {
      setChatLoading(false);
    }
  }

  async function onClearChat() {
    await clearChatHistory(docId);
    setChatMessages([]);
  }

  async function onDeleteDoc() {
    const ok = window.confirm("Delete this document and all derived data (summary, flashcards, chat)?");
    if (!ok) return;
    try {
      await deleteDocument(docId);
      await qc.invalidateQueries({ queryKey: ["documents"] });
      navigate("/");
    } catch {
      alert("Failed to delete document.");
    }
  }

  if (!doc) return <div className="opacity-70">Document not found.</div>;

  const summaryText = latestSummary?.summary || null;
  const hasFlashcards = (flashcardData?.flashcards?.length || 0) > 0;
  const videos = videosData?.videos || [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0 flex flex-col gap-2">
          <h1 className="text-xl font-semibold whitespace-normal break-words [overflow-wrap:anywhere] leading-snug">
            {doc.title}
          </h1>
          <div className="flex flex-wrap gap-3">
            {!summaryText ? (
              <button
                className={`btn btn-primary ${summGenLoading ? "btn-disabled" : ""}`}
                onClick={() => doGenerateSummary(false)}
              >
                {summGenLoading ? "Summarizing..." : "Generate Summary"}
              </button>
            ) : (
              <button
                className={`btn btn-outline ${summGenLoading ? "btn-disabled" : ""}`}
                onClick={() => doGenerateSummary(true)}
              >
                {summGenLoading ? "Regenerating..." : "Regenerate Summary"}
              </button>
            )}

            {!hasFlashcards ? (
              <button
                className={`btn btn-primary ${fcGenLoading ? "btn-disabled" : ""}`}
                onClick={() => doGenerateFlashcards(false)}
              >
                {fcGenLoading ? "Generating..." : "Generate Flashcards"}
              </button>
            ) : (
              <button
                className={`btn btn-outline ${fcGenLoading ? "btn-disabled" : ""}`}
                onClick={() => doGenerateFlashcards(true)}
              >
                {fcGenLoading ? "Regenerating..." : "Regenerate Flashcards"}
              </button>
            )}
          </div>
        </div>

        <button className="btn btn-square btn-ghost shrink-0" title="Delete document" onClick={onDeleteDoc}>
          <Trash2 className="h-5 w-5" />
        </button>
      </div>

      {/* Collapsible Summary */}
      <details className="collapse collapse-arrow bg-base-100 shadow" open>
        <summary className="collapse-title text-lg font-medium">Summary</summary>
        <div className="collapse-content">
          {summaryText ? (
            <p className="text-sm whitespace-pre-wrap">{summaryText}</p>
          ) : (
            <div className="opacity-70">No summary generated yet.</div>
          )}
        </div>
      </details>

      {/* Collapsible Flashcards */}
      <details className="collapse collapse-arrow bg-base-100 shadow" open>
        <summary className="collapse-title text-lg font-medium">Flashcards</summary>
        <div className="collapse-content">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {fcLoadingFetch && <div className="opacity-70">Loading flashcards...</div>}
            {flashcardData?.flashcards?.map((fc) => (
              <div key={fc.id} className="card bg-base-100 border shadow-sm">
                <div className="card-body gap-2">
                  <div className="text-sm font-medium whitespace-normal break-words [overflow-wrap:anywhere] leading-snug">
                    {fc.question}
                  </div>
                  <div className="text-xs opacity-80 whitespace-pre-wrap">{fc.answer}</div>
                </div>
              </div>
            ))}
            {!fcLoadingFetch && (flashcardData?.flashcards?.length || 0) === 0 && (
              <div className="opacity-70">No flashcards yet.</div>
            )}
          </div>
        </div>
      </details>

      {/* Collapsible Related Videos */}
      <details className="collapse collapse-arrow bg-base-100 shadow" open>
        <summary className="collapse-title text-lg font-medium">Related Videos</summary>
        <div className="collapse-content">
          <div className="flex items-center justify-end mb-3">
            <button
              className="btn btn-outline btn-sm"
              onClick={() => getRelatedVideos(docId, { force: true }).then(() => refetchVideos())}
            >
              <RefreshCw className={`h-4 w-4 ${videosLoading ? "animate-spin" : ""}`} />
              <span className="ml-2">Refresh</span>
            </button>
          </div>

          {videosLoading && <div className="opacity-70 text-sm">Finding videos...</div>}

          {!!videos.length ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {videos.map((v) => (
                <a
                  key={v.videoId}
                  href={v.url}
                  target="_blank"
                  rel="noreferrer"
                  className="card bg-base-100 border hover:shadow-md transition"
                >
                  <figure className="aspect-video overflow-hidden">
                    {v.thumbnail ? (
                      <img src={v.thumbnail} alt={v.title} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full bg-base-200" />
                    )}
                  </figure>
                  <div className="card-body p-3 gap-2">
                    <div className="text-sm font-medium whitespace-normal break-words [overflow-wrap:anywhere] leading-snug">
                      {v.title}
                    </div>
                    <div className="text-xs opacity-70">{v.channelTitle}</div>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="opacity-70 text-sm">No suggestions yet. Generate a summary and click Refresh.</div>
          )}
        </div>
      </details>

      {/* Chat (kept always visible) */}
      <div className="card bg-base-100 shadow">
        <div className="card-body gap-4">
          <div className="flex items-center justify-between">
            <h2 className="card-title">Chat with Document</h2>
            <button className="btn btn-outline btn-sm" onClick={onClearChat}>Clear History</button>
          </div>
          <div className="h-72 overflow-y-auto scroll-thin flex flex-col gap-3">
            {chatMessages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[70%] px-3 py-2 rounded-md text-sm shadow-sm whitespace-pre-wrap ${
                  m.role === "user" ? "bg-primary text-primary-content ml-auto" : "bg-base-200"
                }`}
              >
                {m.text}
              </div>
            ))}
            {chatLoading && <div className="text-xs opacity-70">Thinking...</div>}
          </div>
          <div className="flex gap-2">
            <input
              className="input input-bordered w-full"
              placeholder="Ask a question..."
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendChat()}
            />
            <button className="btn btn-primary" disabled={chatLoading} onClick={sendChat}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}