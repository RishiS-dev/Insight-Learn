import { NavLink } from "react-router-dom";

const linkCls = ({ isActive }) =>
  `rounded-lg max-w-full ${
    isActive
      ? "bg-primary/10 text-primary font-medium"
      : "text-base-content/70 hover:bg-base-200"
  }`;

export default function Sidebar({ documents }) {
  return (
    <aside className="w-64 border-r bg-base-100 h-full">
      <ul className="menu p-4 gap-1">
        <li className="menu-title">Documents</li>
        {documents?.map((doc) => (
          <li key={doc.id} className="max-w-full">
            <NavLink to={`/documents/${doc.id}`} className={linkCls}>
              {/* Force long names to wrap nicely even without spaces */}
              <span className="block max-w-full whitespace-normal break-words [overflow-wrap:anywhere] leading-snug">
                {doc.title}
              </span>
            </NavLink>
          </li>
        ))}
      </ul>
    </aside>
  );
}