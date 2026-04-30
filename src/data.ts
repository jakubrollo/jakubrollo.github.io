export type CelestialBody = {
  id: string;
  name: string;
  type: 'planet' | 'moon';
  color: string;
  glowColor?: string;
  labelColor?: string;
  size: number;
  content: string;
  moons?: CelestialBody[];
  distance?: number;
  orbitSpeed?: number;
  link?: string;
};

export type System = CelestialBody & {
  x: number;
  y: number;
};

export const UNIVERSE: System[] = [
  {
    id: 'about',
    type: 'planet',
    name: 'About Me',
    color: 'bg-gradient-to-br from-blue-600 to-indigo-900 border border-blue-400/30',
    glowColor: 'rgba(59, 130, 246, 0.4)', // blue-500
    labelColor: 'text-blue-300',
    size: 180,
    x: 1200,
    y: 1500,
    content: "I'm a Frontend Developer and UI/UX Designer who loves building immersive digital experiences. The web is essentially a vast universe of information, and I enjoy creating the telescopes (and sometimes spaceships) that help users navigate it. My stack mainly consists of React, TypeScript, and modern CSS tooling.",
    link: './cv_test.html',
    moons: [
      {
        id: 'skills',
        type: 'moon',
        name: 'Tech Stack',
        color: 'bg-slate-300',
        glowColor: 'rgba(203, 213, 225, 0.4)',
        size: 35,
        content: "React, TypeScript, Next.js, WebGL/Three.js, Framer Motion, Tailwind CSS, Node.js.",
        distance: 160,
        orbitSpeed: 30
      },
      {
        id: 'experience',
        type: 'moon',
        name: 'History',
        color: 'bg-slate-400',
        glowColor: 'rgba(148, 163, 184, 0.4)',
        size: 25,
        content: "Over 5 years of crafting frontends for agencies and product companies, focusing on interactive data visualization and experimental UI.",
        distance: 210,
        orbitSpeed: 45
      }
    ]
  },
  {
    id: 'projects',
    type: 'planet',
    name: 'Projects',
    color: 'bg-gradient-to-br from-amber-700 to-orange-950 border border-amber-400/20',
    glowColor: 'rgba(245, 158, 11, 0.4)', // amber-500
    labelColor: 'text-amber-200',
    size: 280,
    x: 2300,
    y: 1000,
    content: "My projects span from interactive data dashboards to creative coding experiments. I try to combine robust engineering with high-fidelity visuals. Each satellite orbiting this system represents a key project I've shipped.",
    moons: [
      {
        id: 'proj1',
        type: 'moon',
        name: 'Nebula Protocol',
        color: 'bg-slate-300',
        glowColor: 'rgba(203, 213, 225, 0.4)',
        size: 50,
        content: "A decentralized finance dashboard with real-time token tracking. Built with React and WebSockets, rendering thousands of transactions smoothly.",
        distance: 260,
        orbitSpeed: 35
      },
      {
        id: 'proj2',
        type: 'moon',
        name: 'Astro Type',
        color: 'bg-slate-400',
        glowColor: 'rgba(148, 163, 184, 0.4)',
        size: 45,
        content: "An experimental typography tool that generates kinetic text animations. Users can export directly to video or Lottie format.",
        distance: 350,
        orbitSpeed: 50
      },
      {
        id: 'proj3',
        type: 'moon',
        name: 'Void Runner',
        color: 'bg-slate-500',
        glowColor: 'rgba(100, 116, 139, 0.4)',
        size: 35,
        content: "A WebGL-based browser game where you dodge debris in a procedurally generated asteroid belt. Uses Three.js and custom shaders.",
        distance: 430,
        orbitSpeed: 65
      }
    ]
  },
  {
    id: 'contact',
    type: 'planet',
    name: 'Contact',
    color: 'bg-gradient-to-br from-rose-800 to-black border border-rose-400/40',
    glowColor: 'rgba(244, 63, 94, 0.4)', // rose-500
    labelColor: 'text-rose-300',
    size: 140,
    x: 2800,
    y: 2200,
    content: "Hailing frequencies are open. Feel free to transmit a message if you'd like to collaborate, talk shop, or just say hello.\n\nEmail: hello@example.space\nTwitter: @cosmic_dev",
    moons: []
  }
];
