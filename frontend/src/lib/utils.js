import { clsx } from "clsx";
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const RELATIVE_UNITS = [
  ["year", 365 * 24 * 60 * 60],
  ["month", 30 * 24 * 60 * 60],
  ["week", 7 * 24 * 60 * 60],
  ["day", 24 * 60 * 60],
  ["hour", 60 * 60],
  ["minute", 60],
];

// Feeds read better as "3 hours ago" than as a bare date -- most posts and
// coin awards are recent enough that the date alone says nothing useful.
// Anything older than a year falls back to the absolute date.
export function formatRelativeTime(value) {
  const then = new Date(value);
  if (Number.isNaN(then.getTime())) return "";

  const seconds = Math.round((Date.now() - then.getTime()) / 1000);
  if (seconds < 45) return "just now";
  if (seconds >= RELATIVE_UNITS[0][1]) return then.toLocaleDateString();

  const formatter = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  for (const [unit, unitSeconds] of RELATIVE_UNITS) {
    if (Math.abs(seconds) >= unitSeconds) {
      return formatter.format(-Math.round(seconds / unitSeconds), unit);
    }
  }
  return formatter.format(-seconds, "second");
}
