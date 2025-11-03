import api from "./client";

export const getMotivationToday = async () => {
  const { data } = await api.get("/motivation/today");
  return data?.quote ?? { text: "Keep going!", author: "Unknown", source: "local" };
};