import { useMemo } from 'react';

export function SpaceBackground({ width, height }: { width: number; height: number }) {
  const stars = useMemo(() => {
    return Array.from({ length: 800 }).map(() => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.8 + 0.2,
      twinkleSpeed: Math.random() * 4 + 2,
    }));
  }, [width, height]);

  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none bg-[radial-gradient(circle_at_50%_50%,#080b1a_0%,#020205_100%)]">
      {/* Subtle nebula gradients removed as they were replaced by the main space background in the theme */}

      {stars.map((star, i) => (
        <div
          key={i}
          className="absolute bg-white rounded-full twinkle"
          style={{
            left: star.x,
            top: star.y,
            width: star.size,
            height: star.size,
            opacity: star.opacity,
            '--twinkle-duration': `${star.twinkleSpeed}s`,
          } as any}
        />
      ))}
    </div>
  );
}
