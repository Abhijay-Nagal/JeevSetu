import React from 'react';
import { cn } from "../../lib/utils";

export default function ShinyText({ text, className = "" }) {
  return (
    <span
      className={`inline-block bg-clip-text text-transparent bg-[linear-gradient(110deg,#F4C430,45%,#F8F6E9,55%,#F4C430)] bg-[length:250%_100%] animate-shiny-text ${className}`}
    >
      {text}
    </span>
  );
}
