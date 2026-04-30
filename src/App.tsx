import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence, useMotionValue, animate, useMotionValueEvent } from "motion/react";
import { SpaceBackground } from "./components/SpaceBackground";
import { TelescopeHUD } from "./components/TelescopeHUD";
import { PlanetSystem } from "./components/PlanetSystem";
import { UNIVERSE, CelestialBody, System } from "./data";
import { Locate, ArrowLeft } from "lucide-react";

export default function App() {
  const [subPage, setSubPage] = useState<CelestialBody | null>(null);
  const [activePlanetId, setActivePlanetId] = useState(UNIVERSE[0].id);
  const activePlanetRef = useRef(UNIVERSE[0].id);
  
  const [trackedId, setTrackedId] = useState<string | null>(null);
  const trackBodyRef = useRef<HTMLElement | null>(null);

  const galaxyWidth = 4000;
  const galaxyHeight = 4000;

  const initialPanX = typeof window !== 'undefined' ? (window.innerWidth / 2 - UNIVERSE[0].x) : -1000;
  const initialPanY = typeof window !== 'undefined' ? (window.innerHeight / 2 - UNIVERSE[0].y) : -1000;

  const x = useMotionValue(initialPanX);
  const y = useMotionValue(initialPanY);

  const centerOn = useCallback((body: System | CelestialBody) => {
    if ('x' in body && 'y' in body) {
      const ww = window.innerWidth;
      const wh = window.innerHeight;
      animate(x, ww / 2 - body.x, { type: 'spring', damping: 25, stiffness: 120 });
      animate(y, wh / 2 - body.y, { type: 'spring', damping: 25, stiffness: 120 });
      setActivePlanetId(body.id);
      activePlanetRef.current = body.id;
    }
  }, [x, y]);

  useEffect(() => {
    centerOn(UNIVERSE[0]);
  }, [centerOn]);

  const checkClosestPlanet = useCallback((currentX: number, currentY: number) => {
    const ww = window.innerWidth;
    const wh = window.innerHeight;
    const centerX = ww / 2 - currentX;
    const centerY = wh / 2 - currentY;

    let closest = activePlanetRef.current;
    let minDistance = Infinity;

    for (const p of UNIVERSE) {
      const dist = Math.sqrt(Math.pow(p.x - centerX, 2) + Math.pow(p.y - centerY, 2));
      if (dist < minDistance) {
        minDistance = dist;
        closest = p.id;
      }
    }

    if (closest !== activePlanetRef.current && minDistance < 1000) {
       activePlanetRef.current = closest;
       setActivePlanetId(closest);
    }
  }, []);

  useMotionValueEvent(x, "change", (latestX) => checkClosestPlanet(latestX, y.get()));
  useMotionValueEvent(y, "change", (latestY) => checkClosestPlanet(x.get(), latestY));

  const startTracking = useCallback((el: HTMLElement, id: string) => {
    trackBodyRef.current = el;
    setTrackedId(id);
  }, []);

  const stopTracking = useCallback(() => {
    trackBodyRef.current = null;
    setTrackedId(null);
  }, []);

  useEffect(() => {
    let animationFrameId: number;
    const loop = () => {
      if (trackBodyRef.current && !subPage) {
        const rect = trackBodyRef.current.getBoundingClientRect();
        const ww = window.innerWidth;
        const wh = window.innerHeight;
        
        const elCx = rect.left + rect.width / 2;
        const elCy = rect.top + rect.height / 2;
        
        const dx = elCx - ww/2;
        const dy = elCy - wh/2;
        
        if (Math.abs(dx) > 1 || Math.abs(dy) > 1) {
          x.set(x.get() - dx * 0.08);
          y.set(y.get() - dy * 0.08);
        }
      }
      animationFrameId = requestAnimationFrame(loop);
    };
    loop();
    return () => cancelAnimationFrame(animationFrameId);
  }, [x, y, subPage]);

  const isScrolling = useRef(false);
  useEffect(() => {
    const onWheel = (e: WheelEvent) => {
      if (isScrolling.current || subPage) return;
      if (Math.abs(e.deltaY) < 30) return;

      const currentIndex = UNIVERSE.findIndex(p => p.id === activePlanetId);
      let nextIndex = currentIndex;

      if (e.deltaY > 0) {
        nextIndex = Math.min(currentIndex + 1, UNIVERSE.length - 1);
      } else {
        nextIndex = Math.max(currentIndex - 1, 0);
      }

      if (nextIndex !== currentIndex) {
        isScrolling.current = true;
        const nextPlanet = UNIVERSE[nextIndex];
        centerOn(nextPlanet);
        setTimeout(() => {
          isScrolling.current = false;
        }, 800);
      }
    };
    
    window.addEventListener('wheel', onWheel, { passive: false });
    return () => window.removeEventListener('wheel', onWheel);
  }, [activePlanetId, subPage, centerOn]);

  return (
    <div className="w-screen h-screen bg-[#020205] overflow-hidden relative text-white font-sans">
      <TelescopeHUD />

      <motion.div
        drag
        onPointerDown={stopTracking}
        dragConstraints={{
          left: -(galaxyWidth - (typeof window !== 'undefined' ? window.innerWidth : 1000) + 200),
          right: 200,
          top: -(galaxyHeight - (typeof window !== 'undefined' ? window.innerHeight : 1000) + 200),
          bottom: 200
        }}
        style={{ x, y, width: galaxyWidth, height: galaxyHeight }}
        className="absolute top-0 left-0 cursor-grab active:cursor-grabbing"
      >
        <motion.div 
           className="w-full h-full relative"
           animate={{
             filter: subPage ? 'blur(10px) brightness(0.5)' : 'blur(0px) brightness(1)',
             scale: subPage ? 0.95 : 1
           }}
           transition={{ duration: 0.8, ease: "easeOut" }}
        >
          <SpaceBackground width={galaxyWidth} height={galaxyHeight} />

          {UNIVERSE.map((system) => (
            <PlanetSystem 
              key={system.id} 
              system={system} 
              onSelect={(body) => {
                if (body.link) {
                  window.location.href = body.link;
                } else {
                  setSubPage(body);
                }
              }} 
              onStartTrack={startTracking}
              trackedId={trackedId}
            />
          ))}
        </motion.div>
      </motion.div>

      {/* Navigation Control Panel */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 bg-slate-900/80 backdrop-blur-[12px] border border-white/10 px-8 py-3 rounded-full flex gap-10 items-center">
         <div className="flex items-center gap-2 text-white/50 pr-6 border-r border-white/10">
           <Locate className="w-4 h-4" />
           <span className="font-bold text-[11px] tracking-[0.2em] uppercase hidden sm:block">Nav_Sys</span>
         </div>
         <div className="flex gap-10 font-bold text-[11px] tracking-[0.2em] uppercase overflow-x-auto whitespace-nowrap scrollbar-hide">
           {UNIVERSE.map((p, i) => (
             <button
               key={p.id}
               onClick={() => centerOn(p)}
               className={`transition-colors ${activePlanetId === p.id ? 'text-white' : 'text-white/50 hover:text-white'}`}
             >
               0{i + 1}. {p.name}
             </button>
           ))}
         </div>
      </div>

      {/* Subpage Overlay */}
      <AnimatePresence>
        {subPage && (
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 50 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-xl flex flex-col items-center pt-32 px-4 md:px-8 overflow-y-auto"
          >
            <button 
              onClick={() => setSubPage(null)}
              className="fixed top-8 left-8 md:top-12 md:left-12 text-white/50 hover:text-white flex items-center gap-2 font-bold text-[11px] tracking-[0.2em] uppercase transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Return to Orbit
            </button>
            <div className="max-w-3xl w-full pb-32">
              <div className="flex items-center gap-6 mb-8">
                <div className={`w-16 h-16 rounded-full ${subPage.color} shadow-[0_0_30px_rgba(255,255,255,0.1)] planet-base flex-shrink-0`}></div>
                <div>
                   <h1 className="text-4xl md:text-5xl font-bold text-white tracking-tight">{subPage.name}</h1>
                   <div className="text-[11px] font-bold text-blue-400 uppercase tracking-[0.2em] mt-2">
                     Classification: {subPage.type === 'planet' ? 'Primary Celestial Body' : 'Orbital Satellite'}
                   </div>
                </div>
              </div>
              <div className="h-[1px] w-full bg-white/10 mb-12"></div>
              <div className="text-slate-300 text-lg leading-relaxed font-light whitespace-pre-wrap">
                {subPage.content}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
