import api from "./client";

export const getRelatedVideos = (docId, { limit = 6, force = false } = {}) =>
  api.get(`/videos/${docId}`, { params: { limit, force } }).then(r => r.data);