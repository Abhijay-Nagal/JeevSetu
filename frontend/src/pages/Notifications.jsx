import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, Coins, Heart, Loader2, MessageCircle, RefreshCw, Sparkles, ClipboardCheck } from "lucide-react";
import ShinyText from "../components/ui/ShinyText";
import { api } from "../lib/api";
import { formatRelativeTime } from "../lib/utils";

export const route = { layout: "app" };

const TYPE_STYLES = {
  comment: { icon: MessageCircle, label: "Comment", tint: "bg-[#2196F3]/10 text-[#1565C0]" },
  like: { icon: Heart, label: "Like", tint: "bg-[#E91E63]/10 text-[#AD1457]" },
  reward: { icon: Coins, label: "Reward", tint: "bg-[#F4C430]/20 text-[#8a6d00]" },
  status: { icon: ClipboardCheck, label: "Update", tint: "bg-[#81C784]/20 text-[#2E7D32]" },
  welcome: { icon: Sparkles, label: "Welcome", tint: "bg-[#9C27B0]/10 text-[#6A1B9A]" },
};

export default function Notifications() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  async function load() {
    setRefreshing(true);
    setError("");
    try {
      setItems(await api.getNotifications());
    } catch (err) {
      setError(err.message);
    } finally {
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="mx-auto max-w-4xl pb-24">
      <div className="mb-8 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">
            <ShinyText text="Notifications" variant="green" />
          </h1>
          <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">
            Stay updated on your community activity and submissions.
          </p>
        </div>
        <button
          onClick={load}
          disabled={refreshing}
          className="mt-2 flex shrink-0 items-center gap-2 rounded-xl border border-[#0B3D2E]/15 bg-white px-3 py-2 text-sm font-medium transition hover:border-[#F4C430] disabled:opacity-50"
        >
          <RefreshCw size={15} className={refreshing ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {error && <div className="mb-4 rounded-xl border border-red-100 bg-red-50 p-4 text-red-700">{error}</div>}

      {items === null && !error && (
        <div className="flex justify-center py-16 text-[#0B3D2E]/40">
          <Loader2 size={24} className="animate-spin" />
        </div>
      )}

      {items?.length === 0 && (
        <div className="rounded-2xl border border-dashed border-[#0B3D2E]/20 bg-white/60 p-10 text-center">
          <Bell size={32} className="mx-auto mb-3 text-[#0B3D2E]/30" />
          <p className="font-semibold">You're all caught up</p>
          <p className="mt-1 text-sm text-[#0B3D2E]/60">
            Likes, comments and rewards will show up here.{" "}
            <Link to="/explore-communities" className="font-semibold text-[#2E7D32] hover:underline">
              Share a sighting
            </Link>{" "}
            to get started.
          </p>
        </div>
      )}

      <ul className="space-y-3">
        {items?.map((item) => {
          const style = TYPE_STYLES[item.type] || TYPE_STYLES.status;
          const Icon = style.icon;
          const body = (
            <div className="relative z-10 flex gap-4 rounded-2xl border border-[#0B3D2E]/10 bg-white/70 p-5 shadow-sm backdrop-blur-md transition hover:border-[#0B3D2E]/25">
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full ${style.tint}`}>
                <Icon size={18} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-3">
                  <h3 className="font-bold text-[#0B3D2E]">{item.title}</h3>
                  <span className="shrink-0 rounded-full bg-[#0B3D2E]/5 px-2 py-1 text-xs text-[#0B3D2E]/60">
                    {style.label}
                  </span>
                </div>
                <p className="mt-1 break-words text-sm text-[#0B3D2E]/80">{item.message}</p>
                <time
                  dateTime={item.created_at}
                  title={new Date(item.created_at).toLocaleString()}
                  className="mt-2 block text-xs text-[#0B3D2E]/50"
                >
                  {formatRelativeTime(item.created_at)}
                </time>
              </div>
            </div>
          );
          return (
            <li key={item.id}>
              {item.link ? (
                <Link to={item.link} className="block rounded-2xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F4C430]">
                  {body}
                </Link>
              ) : (
                body
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
