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
  const isDraggingRef = useRef(false);

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

  const checkClosestPlanet = useCallback(() => {
    const ww = window.innerWidth;
    const wh = window.innerHeight;
    const centerX = ww / 2;
    const centerY = wh / 2;

    const planetElements = document.querySelectorAll('.planet-base');
    let minDistance = Infinity;
    let closestId: string | null = null;
    let closestEl: HTMLElement | null = null;

    planetElements.forEach((el) => {
      const rect = el.getBoundingClientRect();
      const elCx = rect.left + rect.width / 2;
      const elCy = rect.top + rect.height / 2;
      const dist = Math.sqrt(Math.pow(elCx - centerX, 2) + Math.pow(elCy - centerY, 2));

      if (dist < minDistance) {
        minDistance = dist;
        closestId = (el as HTMLElement).dataset.id || null;
        closestEl = el as HTMLElement;
      }
    });

    if (closestId && closestId !== activePlanetRef.current && minDistance < 1000) {
       // Only update nav cluster for main systems, but we can just set it
       activePlanetRef.current = closestId;
       setActivePlanetId(closestId);
    }

    // Auto-track logic
    if (!isDraggingRef.current && !subPage) {
      // If we are not currently tracking anything, try to snap to the closest if within radius
      if (!trackedId && minDistance < 250 && closestId) {
        setTrackedId(closestId);
      }
      // Note: We no longer auto-break the lock based on distance. 
      // The lock is only broken when the user clicks and drags the galaxy (onDragStart).
      // This ensures that clicking/hovering a distant planet guarantees the camera travels all the way to it!
    }
  }, [trackedId, subPage]);

  // Use passive requestAnimationFrame to check proximity instead of motion values directly since Moons move
  useEffect(() => {
    let animationFrameId: number;
    const proximityLoop = () => {
      checkClosestPlanet();
      animationFrameId = requestAnimationFrame(proximityLoop);
    };
    animationFrameId = requestAnimationFrame(proximityLoop);
    return () => cancelAnimationFrame(animationFrameId);
  }, [checkClosestPlanet]);

  const startTracking = useCallback((el: HTMLElement, id: string) => {
    // Allows instant manual click/hover snap
    setTrackedId(id);
  }, []);

  const stopTracking = useCallback(() => {
    // Empty, don't break lock on pointer down 
  }, []);

  useEffect(() => {
    let animationFrameId: number;
    const loop = () => {
      if (trackedId && !subPage) {
        const el = document.querySelector(`[data-id="${trackedId}"]`) as HTMLElement;
        if (el) {
          const ww = window.innerWidth;
          const wh = window.innerHeight;
          
          // Get screen-space coordinates of the locked element
          const rect = el.getBoundingClientRect();
          const elCx = rect.left + rect.width / 2;
          const elCy = rect.top + rect.height / 2;
          
          // Distance from screen center
          const dx = elCx - ww/2;
          const dy = elCy - wh/2;
          
          // Gently drag the galaxy to keep it centered
          if (Math.abs(dx) > 1 || Math.abs(dy) > 1) {
            const ease = isDraggingRef.current ? 0.0 : 0.15; // Track faster when not dragging
            x.set(x.get() - dx * ease);
            y.set(y.get() - dy * ease);
          }
        }
      }
      animationFrameId = requestAnimationFrame(loop);
    };
    loop();
    return () => cancelAnimationFrame(animationFrameId);
  }, [x, y, subPage, trackedId]);

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
        onDragStart={() => {
          isDraggingRef.current = true;
          // Temporarily break tracking so we don't fight the user drag
          setTrackedId(null);
        }}
        onDragEnd={() => {
          isDraggingRef.current = false;
        }}
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

      {/* Subpage Overlay: Half screen on the right */}
      <AnimatePresence>
        {subPage && (
          <motion.div
            initial={{ opacity: 0, x: "100%" }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed top-0 right-0 h-full w-full md:w-[60%] lg:w-[45%] xl:w-[35%] z-[100] bg-slate-950/95 backdrop-blur-3xl shadow-2xl border-l border-white/5 flex flex-col pt-24 px-8 md:px-12 overflow-y-auto"
          >
            <button 
              onClick={() => setSubPage(null)}
              className="absolute top-8 left-8 text-white/50 hover:text-white flex items-center gap-2 font-bold text-[11px] tracking-[0.2em] uppercase transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Close
            </button>
            <div className="w-full pb-32">
              <div className="flex flex-col gap-6 mb-8 pt-4">
                <div className={`w-24 h-24 rounded-full ${subPage.color} shadow-[0_0_40px_rgba(255,255,255,0.1)] planet-base flex-shrink-0 self-start`}></div>
                <div>
                   <h1 className="text-3xl md:text-4xl font-bold text-white tracking-tight leading-tight">{subPage.name}</h1>
                   <div className="text-[11px] font-bold text-blue-400 uppercase tracking-[0.2em] mt-3">
                     Classification: {subPage.type === 'planet' ? 'Primary Celestial Body' : 'Orbital Satellite'}
                   </div>
                </div>
              </div>
              <div className="h-[1px] w-full bg-white/10 mb-8"></div>
              <div className="text-slate-300 text-base leading-relaxed font-light whitespace-pre-wrap">
                {subPage.content}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
