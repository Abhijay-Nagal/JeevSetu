import { useState } from "react";
import SpotlightCard from "../ui/SpotlightCard";

export default function CommunityCard({ community, isMember, onOpen, onJoin, onLeave }) {
  // Join/leave both hit the network and both award or revoke coins, so the
  // button has to stop taking clicks until the request settles -- an
  // impatient double-click used to fire two joins for the same community.
  const [busy, setBusy] = useState(false);

  async function run(action) {
    if (busy || !action) return;
    setBusy(true);
    try {
      await action(community);
    } catch {
      // The page that owns the handler surfaces the message; the card just
      // needs to come back out of its pending state.
    } finally {
      setBusy(false);
    }
  }

  return (
    <SpotlightCard className="p-0 border-none bg-transparent hover:translate-y-0 shadow-none hover:shadow-none mb-4 group">
      <div className="flex items-center justify-between gap-4 rounded-xl border border-[#0B3D2E]/10 bg-white p-4 transition-colors group-hover:border-[#0B3D2E]/20">
        <button onClick={() => onOpen(community)} className="min-w-0 flex-1 text-left">
          <h3 className="font-semibold">{community.name}</h3>
          {community.description && <p className="mt-1 text-sm opacity-70">{community.description}</p>}
        </button>

        {isMember ? (
          <button
            onClick={() => run(onLeave)}
            disabled={busy}
            className="shrink-0 rounded-lg border border-[#0B3D2E]/20 px-3 py-1.5 text-sm transition hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {busy ? "Leaving..." : "Leave"}
          </button>
        ) : (
          <button
            onClick={() => run(onJoin)}
            disabled={busy}
            className="shrink-0 rounded-lg bg-[#0B3D2E] px-3 py-1.5 text-sm text-white transition hover:bg-[#0B3D2E]/90 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {busy ? "Joining..." : "Join"}
          </button>
        )}
      </div>
    </SpotlightCard>
  );
}
