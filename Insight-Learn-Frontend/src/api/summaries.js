import api from "./client";

export const getLatestSummary = (docId) =>
  api.get(`/summaries/latest/${docId}`).then(r => r.data);

export const listSummaries = (docId) =>
  api.get(`/summaries/${docId}`).then(r => r.data);

export const generateSummary = (docId, { force = false } = {}) =>
  api.post(`/summaries/generate/${docId}`, null, { params: { force } }).then(r => r.data);