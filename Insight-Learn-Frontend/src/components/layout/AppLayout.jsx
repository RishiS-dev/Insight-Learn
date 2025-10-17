import { Outlet } from "react-router-dom";
import TopBar from "./TopBar";
import Sidebar from "./Sidebar";
import { useQuery } from "@tanstack/react-query";
import { listDocuments } from "../../api/documents";

export default function AppLayout() {
  const { data } = useQuery({
    queryKey: ["documents"],
    queryFn: listDocuments,
    staleTime: 30_000
  });

  return (
    <div className="flex flex-col min-h-screen">
      <TopBar />
      <div className="flex flex-1">
        <Sidebar documents={data?.documents || []} />
        <main className="flex-1 p-6 overflow-y-auto scroll-thin">
          <Outlet />
        </main>
      </div>
    </div>
  );
}