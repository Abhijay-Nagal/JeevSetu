import React from 'react';
import ShinyText from "../components/ui/ShinyText";

export const route = { layout: "app" };

export default function Notifications() {
  return (
    <div className="mx-auto max-w-4xl pb-24">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight">
          <ShinyText text="Notifications" variant="green" />
        </h1>
        <p className="mt-3 text-lg opacity-80 text-[#0B3D2E]">
          Stay updated on your community activity and submissions.
        </p>
      </div>

      <div className="space-y-4">
        {/* Notification 1 */}
        <div className="relative z-10 rounded-2xl border border-[#0B3D2E]/10 bg-white/70 backdrop-blur-md p-6 shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-[#0B3D2E]">New Community Challenge</h3>
            <span className="text-xs text-[#0B3D2E]/60 bg-[#0B3D2E]/5 px-2 py-1 rounded-full">New</span>
          </div>
          <p className="text-sm text-[#0B3D2E]/80 mb-2">
            The Western Ghats Birding community has launched a new weekend challenge: "Spot the Malabar Pied Hornbill". Join now to earn 50 coins!
          </p>
          <span className="text-xs text-[#0B3D2E]/50">2 hours ago</span>
        </div>

        {/* Notification 2 */}
        <div className="relative z-10 rounded-2xl border border-[#0B3D2E]/10 bg-white/70 backdrop-blur-md p-6 shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-[#0B3D2E]">Submission Approved</h3>
            <span className="text-xs text-[#0B3D2E]/60 bg-[#0B3D2E]/5 px-2 py-1 rounded-full">Update</span>
          </div>
          <p className="text-sm text-[#0B3D2E]/80 mb-2">
            Your recent publication "Unusual Nectar-Feeding Bird Recorded in the Eastern Himalayas" has been verified and added to the BNHS records.
          </p>
          <span className="text-xs text-[#0B3D2E]/50">1 day ago</span>
        </div>

        {/* Notification 3 */}
        <div className="relative z-10 rounded-2xl border border-[#0B3D2E]/10 bg-white/70 backdrop-blur-md p-6 shadow-sm">
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-bold text-[#0B3D2E]">Streak Milestone Reached!</h3>
            <span className="text-xs text-[#0B3D2E]/60 bg-[#0B3D2E]/5 px-2 py-1 rounded-full">Achievement</span>
          </div>
          <p className="text-sm text-[#0B3D2E]/80 mb-2">
            Congratulations! You've maintained a 7-day streak answering daily questions. You've been awarded a bonus of 100 coins.
          </p>
          <span className="text-xs text-[#0B3D2E]/50">3 days ago</span>
        </div>
      </div>
    </div>
  );
}
