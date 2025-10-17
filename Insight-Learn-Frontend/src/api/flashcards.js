import api from "./client";

export const generateFlashcards = (docId, num = 5, { force = false } = {}) =>
  api.post(`/flashcards/${docId}`, null, {
    params: { num_cards: num, force }
  }).then(r => r.data);

export const listFlashcards = (docId) =>
  api.get(`/flashcards/list/${docId}`).then(r => r.data);