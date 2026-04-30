import { System, CelestialBody } from "../data";
import { useRef } from "react";

export function PlanetSystem({ 
  system, 
  onSelect,
  onStartTrack,
  trackedId
}: { 
  system: System, 
  onSelect: (body: CelestialBody) => void,
  onStartTrack: (el: HTMLElement, id: string) => void,
  trackedId: string | null
}) {
  const timeoutRef = useRef<NodeJS.Timeout>();

  const handleMouseEnter = (e: React.MouseEvent<HTMLElement>, id: string) => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    const el = e.currentTarget;
    timeoutRef.current = setTimeout(() => {
      onStartTrack(el, id);
    }, 600);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
  };

  const isSystemTracked = trackedId === system.id;

  return (
    <div
      className="absolute rounded-full flex items-center justify-center"
      style={{
        left: system.x,
        top: system.y,
        width: system.size,
        height: system.size,
        transform: "translate(-50%, -50%)",
      }}
    >
      <div
        onClick={(e) => { e.stopPropagation(); onSelect(system); }}
        onMouseEnter={(e) => handleMouseEnter(e, system.id)}
        onMouseLeave={handleMouseLeave}
        className={`relative w-full h-full rounded-full ${system.color} planet-base cursor-pointer z-10 group`}
        style={{ '--glow-color': system.glowColor || 'rgba(255,255,255,0.4)' } as any}
        data-id={system.id}
      >
        {/* Label Always Visible */}
        <div className={`absolute top-[110%] left-1/2 -translate-x-1/2 mt-2 ${system.labelColor || 'text-white'} font-bold text-[11px] tracking-[0.2em] uppercase whitespace-nowrap pointer-events-none`}>
          {system.name}
        </div>

        {/* Hover Info */}
        <div className={`absolute top-[150%] left-1/2 -translate-x-1/2 mt-4 transition-opacity bg-slate-900/95 backdrop-blur-[12px] border border-white/10 text-slate-300 text-xs p-4 rounded-xl w-64 pointer-events-none shadow-[0_0_30px_rgba(0,0,0,0.8)] z-50 ${isSystemTracked ? 'opacity-100 block' : 'opacity-0 hidden group-hover:opacity-100 group-hover:block'}`}>
          <div className="text-[10px] text-slate-500 uppercase tracking-widest mb-2 border-b border-white/10 pb-2">Celestial Info</div>
          <p className="line-clamp-4 leading-relaxed font-light">{system.content}</p>
          <div className="mt-3 text-[10px] text-blue-400 font-bold uppercase tracking-widest">Click to enter orbit &rarr;</div>
        </div>
      </div>

      {/* Orbit Rings and Moons */}
      {system.moons?.map((moon) => {
        const isMoonTracked = trackedId === moon.id;
        return (
          <div
            key={moon.id}
            className="absolute rounded-full border border-dashed border-white/10 pointer-events-none"
            style={{
              width: moon.distance! * 2,
              height: moon.distance! * 2,
            }}
          >
            {/* Orbit Wrapper */}
            <div
              className="absolute top-0 left-0 w-full h-full orbit-container pointer-events-none"
              style={{ "--duration": `${moon.orbitSpeed}s` } as any}
            >
              {/* The Moon itself */}
              <div
                data-id={moon.id}
                className={`absolute rounded-full ${moon.color} planet-base pointer-events-auto cursor-pointer group`}
                style={{
                  width: moon.size,
                  height: moon.size,
                  top: 0,
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  '--glow-color': moon.glowColor || 'rgba(255,255,255,0.4)',
                } as any}
                onClick={(e) => { e.stopPropagation(); onSelect(moon); }}
                onMouseEnter={(e) => handleMouseEnter(e, moon.id)}
                onMouseLeave={handleMouseLeave}
              >
                {/* Counter-rotating tooltip wrapper */}
                <div
                  className="absolute w-full h-full counter-orbit pointer-events-none flex items-center justify-center"
                  style={{ "--duration": `${moon.orbitSpeed}s` } as any}
                >
                    {/* Moon Label Always Visible */}
                    <div className={`absolute top-[130%] opacity-80 ${system.labelColor || 'text-white'} font-bold text-[10px] uppercase tracking-widest whitespace-nowrap`}>
                      {moon.name}
                    </div>

                    {/* Moon Hover Info */}
                    <div className={`absolute top-[200%] transition-opacity bg-slate-900/95 backdrop-blur-[12px] border border-white/10 text-slate-300 text-[10px] p-3 rounded-lg w-48 shadow-[0_0_20px_rgba(0,0,0,0.8)] z-50 text-left ${isMoonTracked ? 'opacity-100 block' : 'opacity-0 hidden group-hover:opacity-100 group-hover:block'}`}>
                       <p className="line-clamp-3 leading-relaxed font-light">{moon.content}</p>
                       <div className="mt-2 text-blue-400 font-bold uppercase tracking-widest text-[9px]">Explore &rarr;</div>
                    </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
