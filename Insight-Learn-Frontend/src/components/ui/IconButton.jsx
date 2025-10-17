import React from "react";

export default function IconButton({
  children,
  onClick,
  title = "",
  ariaLabel = "",
  variant = "outline", // "outline" | "ghost" | "solid"
  size = "md", // "sm" | "md" | "lg"
  className = "",
  disabled = false,
  type = "button",
}) {
  const sizeCls =
    size === "sm"
      ? "h-8 w-8"
      : size === "lg"
      ? "h-12 w-12"
      : "h-10 w-10";

  const variantCls =
    variant === "solid"
      ? "bg-primary text-white hover:bg-primary-hover"
      : variant === "ghost"
      ? "bg-transparent hover:bg-bg-subtle text-text"
      : "border border-border bg-white text-text hover:bg-bg";

  return (
    <button
      type={type}
      onClick={onClick}
      title={title}
      aria-label={ariaLabel || title}
      disabled={disabled}
      className={`${sizeCls} inline-flex items-center justify-center rounded-sm shadow-sm transition-colors ${variantCls} ${disabled ? "opacity-60 cursor-not-allowed" : "cursor-pointer"} ${className}`}
    >
      {children}
    </button>
  );
}