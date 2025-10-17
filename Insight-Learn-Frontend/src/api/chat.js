import api from "./client";

export const chatWithDoc = (docId, query) =>
  api.post(`/chat/${docId}`, null, { params: { query } }).then(r => r.data);

export const clearChatHistory = (docId) =>
  api.delete(`/chat/clear/${docId}`).then(r => r.data);

export const getChatHistory = (docId, limit = 50) =>
  api.get(`/chat/history/${docId}`, { params: { limit } }).then(r => r.data);