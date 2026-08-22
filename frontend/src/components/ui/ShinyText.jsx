import React from 'react';
import { cn } from "../../lib/utils";

export default function ShinyText({ text, className }) {
  return (
    <span
      className={cn(
        "inline-block bg-clip-text text-transparent bg-[linear-gradient(110deg,#0B3D2E,45%,#34d399,55%,#0B3D2E)] bg-[length:250%_100%] animate-shiny-text",
        className
      )}
    >
      {text}
    </span>
  );
}
