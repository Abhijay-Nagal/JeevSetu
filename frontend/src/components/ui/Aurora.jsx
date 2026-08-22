import React from "react";

export default function Aurora({ 
  color1 = "#2E7D32", 
  color2 = "#F4C430", 
  color3 = "#81C784",
  opacity = 0.3
}) {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
      <div 
        className="absolute -inset-[100%]"
        style={{
          opacity,
          filter: "blur(60px)",
          background: `
            radial-gradient(circle at 50% 50%, ${color1} 0%, transparent 40%), 
            radial-gradient(circle at 80% 20%, ${color2} 0%, transparent 40%), 
            radial-gradient(circle at 20% 80%, ${color3} 0%, transparent 40%)
          `,
          animation: 'aurora 20s ease-in-out infinite alternate'
        }}
      />
      <style>{`
        @keyframes aurora {
          0% { 
            transform: scale(1) rotate(0deg) translate(0, 0); 
          }
          33% { 
            transform: scale(1.2) rotate(90deg) translate(5%, 5%); 
          }
          66% { 
            transform: scale(0.9) rotate(180deg) translate(-5%, 5%); 
          }
          100% { 
            transform: scale(1.1) rotate(360deg) translate(0, -5%); 
          }
        }
      `}</style>
    </div>
  );
}
