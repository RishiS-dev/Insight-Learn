import { useQuery } from "@tanstack/react-query";
import { listDocuments, uploadDocument, deleteDocument } from "../api/documents";
import { useState } from "react";
import { Trash2 } from "lucide-react";

export default function DashboardPage() {
  const { data, refetch, isLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
  });
  const [uploading, setUploading] = useState(false);

  async function onFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadDocument(file);
      refetch();
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function onDelete(id) {
    const ok = window.confirm("Delete this document?");
    if (!ok) return;
    await deleteDocument(id);
    refetch();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Your Documents</h2>
        <label className={`btn btn-primary ${uploading ? "btn-disabled" : ""} cursor-pointer`}>
          {uploading ? "Uploading..." : "Upload PDF"}
          <input type="file" accept="application/pdf" className="hidden" onChange={onFile} disabled={uploading} />
        </label>
      </div>

      {isLoading && <p className="opacity-70">Loading...</p>}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.documents?.map((doc) => (
          <div key={doc.id} className="card bg-base-100 shadow">
            <div className="card-body gap-4">
              {/* Wrap long titles on cards */}
              <h3 className="card-title whitespace-normal break-words [overflow-wrap:anywhere] leading-snug">
                {doc.title}
              </h3>
              <div className="card-actions justify-end">
                <button
                  className="btn btn-outline"
                  onClick={() => (window.location.href = `/documents/${doc.id}`)}
                >
                  Open
                </button>
                <button className="btn btn-square btn-ghost" title="Delete" onClick={() => onDelete(doc.id)}>
                  <Trash2 className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        ))}
        {!isLoading && (!data?.documents || data.documents.length === 0) && (
          <div className="opacity-70">No documents yet. Upload one to get started.</div>
        )}
      </div>
    </div>
  );
}