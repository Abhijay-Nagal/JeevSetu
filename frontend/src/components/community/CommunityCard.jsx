export default function CommunityCard({ community, isMember, onOpen, onJoin, onLeave }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-xl border border-[#0B3D2E]/10 bg-white p-4">
      <button onClick={() => onOpen(community)} className="min-w-0 flex-1 text-left">
        <h3 className="font-semibold">{community.name}</h3>
        {community.description && <p className="mt-1 text-sm opacity-70">{community.description}</p>}
      </button>

      {isMember ? (
        <button
          onClick={() => onLeave(community)}
          className="shrink-0 rounded-lg border border-[#0B3D2E]/20 px-3 py-1.5 text-sm"
        >
          Leave
        </button>
      ) : (
        <button
          onClick={() => onJoin(community)}
          className="shrink-0 rounded-lg bg-[#0B3D2E] px-3 py-1.5 text-sm text-white"
        >
          Join
        </button>
      )}
    </div>
  );
}
