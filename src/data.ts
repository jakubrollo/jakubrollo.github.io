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
    content: "AI/GameDev-focused Computer Science student pursuing a Master's degree at Charles University. I have a passion for programming video games, building game engines, and low-level optimization. I'm highly interested in performance-oriented systems, modern machine learning techniques, and utilizing Large Language Models.",
    link: './cv_test.html',
    moons: [
      {
        id: 'skills',
        type: 'moon',
        name: 'Tech Stack',
        color: 'bg-slate-300',
        glowColor: 'rgba(203, 213, 225, 0.4)',
        size: 35,
        content: "Languages: C#, C++, Python, Java. Engines: Unity, Godot. Frameworks & Concepts: PyTorch, Neural Networks, Evolutionary Algorithms, Parallel Computing, OpenGL.",
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
        content: "Process Automation Developer at Hornbach (building VBScript bots for SAP systems) and Board of Directors at Stanislav Sucharda Museum Foundation.",
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
    content: "My projects span cutting-edge AI research to custom game engines and 48-hour game jams. I combine robust, low-level engineering with high-level mechanics. Here are some of my key works orbiting this system.",
    moons: [
      {
        id: 'proj1',
        type: 'moon',
        name: 'Super Mario AI Thesis',
        color: 'bg-slate-300',
        glowColor: 'rgba(203, 213, 225, 0.4)',
        size: 50,
        content: "Bachelor Thesis: Enhanced procedural level generation for Super Mario across three existing studies using perfect agents.",
        distance: 260,
        orbitSpeed: 35
      },
      {
        id: 'proj2',
        type: 'moon',
        name: 'Game Jams',
        color: 'bg-slate-400',
        glowColor: 'rgba(148, 163, 184, 0.4)',
        size: 45,
        content: "Participated in 5 distinct Game Jams. Designed and programmed core mechanics to deliver functional game prototypes under strict 48-hour time constraints.",
        distance: 350,
        orbitSpeed: 50
      },
      {
        id: 'proj3',
        type: 'moon',
        name: 'Murder Mystery AI',
        color: 'bg-purple-500',
        glowColor: 'rgba(168, 85, 247, 0.4)', // purple-500
        size: 40,
        content: "A Python-based AI Murder Mystery generator. It uses Answer Set Programming (Clingo ASP) alongside a CustomTkinter UI to procedurally generate uniquely solvable logical puzzles every time you play.",
        distance: 430,
        orbitSpeed: 25,
        link: 'https://github.com/jakubrollo/jakubrollo.github.io/tree/main/murderMystery'
      },
      {
        id: 'proj4',
        type: 'moon',
        name: 'Custom C++ Engine',
        color: 'bg-slate-500',
        glowColor: 'rgba(100, 116, 139, 0.4)',
        size: 35,
        content: "Built a custom 2D dungeon crawler game handling core rendering and player mechanics using C++ and SFML.",
        distance: 510,
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
    content: "Let's connect!\n\nEmail: jakubrollo10@gmail.com\nGitHub: github.com/jakubrollo\nLocation: Brandýs nad Labem / Prague",
    moons: []
  }
];
