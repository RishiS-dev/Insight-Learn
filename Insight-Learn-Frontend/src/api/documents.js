import api from "./client";

export const listDocuments = () =>
  api.get("/documents/list").then(r => r.data);

export const uploadDocument = file => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  }).then(r => r.data);
};

export const reindexDocument = (docId) =>
  api.post(`/documents/${docId}/reindex`).then(r => r.data); // if you add reindex later

export const deleteDocument = (docId) =>
  api.delete(`/documents/${docId}`).then(r => r.data);