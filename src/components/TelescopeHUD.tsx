export function TelescopeHUD() {
  return (
    <div className="fixed inset-0 pointer-events-none z-40">
      
      {/* CRT Glass Reflection & Vignette */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.6) 80%, rgba(0,0,0,0.95) 100%)',
          boxShadow: 'inset 0 0 100px rgba(0,0,0,1)',
        }}
      ></div>

      {/* CRT Scanlines */}
      <div 
        className="absolute inset-0 opacity-[0.15] mix-blend-overlay pointer-events-none"
        style={{
          background: "linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,0) 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,1))",
          backgroundSize: "100% 4px"
        }}
      ></div>

      {/* Grid Lines */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_80%)] pointer-events-none mix-blend-screen"></div>

      {/* HUD Content Overlay */}
      <div className="absolute inset-0 flex items-center justify-center mix-blend-screen pointer-events-none z-50">
        {/* Crosshairs */}
        <div className="w-[1px] h-[100vh] bg-white/15 absolute left-1/2 -translate-x-1/2"></div>
        <div className="h-[1px] w-[100vw] bg-white/15 absolute top-1/2 -translate-y-1/2"></div>
        
        {/* Ticks on crosshairs */}
        <div className="absolute w-[20px] h-[1px] bg-white/15 left-1/2 -translate-x-1/2 top-[30%]"></div>
        <div className="absolute w-[20px] h-[1px] bg-white/15 left-1/2 -translate-x-1/2 top-[70%]"></div>
        <div className="absolute h-[20px] w-[1px] bg-white/15 top-1/2 -translate-y-1/2 left-[30%]"></div>
        <div className="absolute h-[20px] w-[1px] bg-white/15 top-1/2 -translate-y-1/2 left-[70%]"></div>

        {/* Center Reticle */}
        <div className="w-[120px] h-[120px] rounded-full border border-blue-400/30 absolute pointer-events-none flex items-center justify-center">
           <div className="w-[80px] h-[80px] rounded-full border border-dashed border-white/20 animate-[spin_30s_linear_infinite]"></div>
           <div className="w-1.5 h-1.5 bg-blue-400 rounded-full absolute shadow-[0_0_10px_rgba(96,165,250,1)]"></div>
        </div>

        {/* Tech Overlays */}
        <div className="absolute top-8 left-8 text-blue-400 font-mono text-[10px] uppercase tracking-widest flex flex-col gap-1.5">
          <span className="flex items-center gap-2">SYS_STATUS: NOMINAL</span>
          <span>REC_DEEP_SPACE_9</span>
          <span>OPTICS: ACTIVE</span>
        </div>
        <div className="absolute top-8 right-8 text-red-400 font-mono text-[10px] uppercase tracking-widest flex flex-col gap-1.5 text-right">
          <span>SECTOR: OMEGA-7</span>
          <span>MAGNIFICATION: 400X</span>
        </div>
        <div className="absolute bottom-8 right-8 flex gap-2 items-center">
          <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></div>
          <span className="font-mono text-[10px] text-white/40 uppercase tracking-widest">SYSTEM ONLINE</span>
        </div>
      </div>
    </div>
  );
}
