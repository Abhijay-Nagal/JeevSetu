import React from 'react';
import { cn } from "../../lib/utils";

export default function ShinyText({ text, className = "", variant = "gold" }) {
  const gradient = variant === "green"
    ? "bg-[linear-gradient(110deg,#0B3D2E,45%,#2E7D32,55%,#0B3D2E)]"
    : "bg-[linear-gradient(110deg,#F4C430,45%,#F8F6E9,55%,#F4C430)]";

  return (
    <span
      className={`inline-block bg-clip-text text-transparent ${gradient} bg-[length:250%_100%] animate-shiny-text ${className}`}
    >
      {text}
    </span>
  );
}
