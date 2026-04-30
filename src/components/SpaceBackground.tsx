import { useMemo } from 'react';

export interface Star {
  x: number;
  y: number;
  size: number;
  opacity: number;
  twinkleSpeed: number;
}

export function SpaceBackground({ width, height, stars }: { width: number; height: number; stars?: Star[] }) {
  const generatedStars = useMemo(() => {
    if (stars) return stars;

    // Fallback generation if no shared stars are provided.
    const starCount = 350;
    return Array.from({ length: starCount }).map(() => ({
      x: Math.random() * width,
      y: Math.random() * height,
      size: Math.random() * 2 + 0.5,
      opacity: Math.random() * 0.8 + 0.2,
      twinkleSpeed: Math.random() * 4 + 2,
    }));
  }, [width, height, stars]);

  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">

      {generatedStars.map((star, i) => (
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
