
'use client';

import React, { useState, useEffect, useRef } from 'react';
import { 
  Library, Database, Network, TrendingUp, FileText, Terminal as TerminalIcon,
  ChevronRight, Shield, Tag, FolderOpen, Activity, Cpu, MessageSquare,
  Send, Loader2, Sparkles, BrainCircuit, Upload, Plus, Maximize2,
  BarChart3, PieChart, Users, FileDown, Layers, Zap, X, Eye, FileCode, ImageIcon,
  AlertTriangle, CheckCircle2, Calendar, Search, Globe, Rocket, Monitor, Presentation,
  ChevronLeft, ExternalLink, Award
} from 'lucide-react';
import { postJson } from '@/lib/backend';
import { fetchKpiTargets } from '@/lib/kpi';
import { INITIAL_GENESIS_LOG, INITIAL_PROPOSITIONS, GRAPH_DATA, POTENTIAL_FUNDERS } from './constants';
import { FileStatus, GenesisEntry, Proposition, GraphNode, GraphLink, PotentialUse, RiskLevel, Funder } from './types';
import * as d3 from 'd3';

type AlexandriaChatResponse = {
  reply?: string;
};

const OPERATIONS_DOCS = [
  { label: 'Culture Operating System', path: 'docs/CULTURE_OPERATING_SYSTEM.md' },
  { label: 'KPI Execution Engine', path: 'docs/KPI_EXECUTION_ENGINE.md' },
  { label: 'Revenue Streams Workflow', path: 'docs/REVENUE_STREAMS_WORKFLOW.md' },
  { label: 'Process Workflows', path: 'docs/PROCESS_WORKFLOWS.md' },
  { label: 'Running Success Story', path: 'docs/RUNNING_SUCCESS_STORY.md' },
  { label: 'Operating Index', path: 'docs/OPERATING_INDEX.md' },
];

const LIVE_SERVICES = [
  { label: 'Backend', url: 'https://youtube-ai-backend-71658389068.us-central1.run.app' },
  { label: 'Frontend', url: 'https://youtube-ai-frontend-71658389068.us-central1.run.app' },
  { label: 'Alexandria UI', url: 'https://youtube-ai-frontend-71658389068.us-central1.run.app/alexandria' },
  { label: 'Alexandria API', url: 'https://youtube-ai-backend-71658389068.us-central1.run.app/api/ai/alexandria' },
  { label: 'AutonomaX API (ready)', url: 'https://autonomax-api-lenljbhrqq-uc.a.run.app/ready' },
  { label: 'AutonomaX API (ready)', url: 'https://autonomax-api-71658389068.us-central1.run.app/ready' },
];

// --- Sub-components ---

const SidebarItem = ({ active, icon: Icon, label, onClick }: any) => (
  <button 
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
      active ? 'bg-amber-600/20 text-amber-500 border-l-4 border-amber-600' : 'text-stone-400 hover:bg-stone-800'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium text-sm">{label}</span>
  </button>
);

const ConsoleLine = ({ type, text }: { type: string, text: string }) => (
  <div className="flex gap-3 text-xs font-mono py-0.5">
    <span className="text-stone-500">[{new Date().toLocaleTimeString()}]</span>
    <span className={
      type === 'info' ? 'text-blue-400' : 
      type === 'success' ? 'text-green-400' : 
      type === 'warning' ? 'text-amber-400' : 
      type === 'ai' ? 'text-purple-400' :
      'text-stone-300'
    }>{type.toUpperCase()}</span>
    <span>{text}</span>
  </div>
);

// --- Presentation Components ---

const Slide = ({ children, title, index, total }: { children: React.ReactNode, title: string, index: number, total: number }) => (
  <div className="presentation-slide w-full min-h-[500px] bg-[#1c1917] border border-stone-800 rounded-2xl p-12 flex flex-col relative overflow-hidden shadow-2xl">
    <div className="absolute top-0 right-0 p-8 text-[10px] font-mono text-stone-600">
      SLIDE {index + 1} / {total}
    </div>
    <div className="absolute bottom-0 left-0 w-full h-1 bg-stone-900">
      <div className="h-full bg-amber-600 transition-all duration-500" style={{ width: `${((index + 1) / total) * 100}%` }}></div>
    </div>
    <div className="flex-1 flex flex-col">
      <div className="mb-12">
        <h2 className="text-4xl font-cinzel font-bold text-amber-500 tracking-tighter mb-2">{title}</h2>
        <div className="w-24 h-1 bg-amber-600/30"></div>
      </div>
      <div className="flex-1">
        {children}
      </div>
    </div>
    <div className="mt-8 flex justify-between items-center opacity-30">
      <div className="text-[10px] font-cinzel font-bold tracking-widest text-stone-400">PROJECT ALEXANDRIA PROTOCOL</div>
      <div className="text-[10px] font-mono text-stone-500">PRIVATE & CONFIDENTIAL</div>
    </div>
  </div>
);

const PresentationView = ({ propositions, funders }: { propositions: Proposition[], funders: Funder[] }) => {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [selectedProposition, setSelectedProposition] = useState<Proposition>(propositions[0]);

  const slides = [
    {
      title: "The Executive Mandate",
      content: (
        <div className="grid grid-cols-2 gap-12 items-center h-full">
          <div className="space-y-6">
            <p className="text-2xl text-stone-300 font-light leading-relaxed">
              Synthesizing dormant digital archives into <span className="text-amber-500 font-bold">liquid revenue channels</span> through automated intelligence and strategic orchestration.
            </p>
            <div className="flex gap-4">
              <div className="p-4 bg-stone-900 rounded-xl border border-stone-800 flex-1">
                <div className="text-3xl font-bold text-amber-500">$75K+</div>
                <div className="text-[10px] font-bold text-stone-500 uppercase mt-1">Initial Alpha Valuation</div>
              </div>
              <div className="p-4 bg-stone-900 rounded-xl border border-stone-800 flex-1">
                <div className="text-3xl font-bold text-green-500">300%</div>
                <div className="text-[10px] font-bold text-stone-500 uppercase mt-1">Projected Avg ROI</div>
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="absolute -inset-4 bg-amber-600/5 blur-3xl rounded-full"></div>
            <div className="relative bg-stone-950 p-8 rounded-3xl border border-stone-800 shadow-2xl">
              <div className="flex items-center gap-3 mb-6">
                <BrainCircuit className="text-amber-500" size={32} />
                <span className="text-xl font-cinzel font-bold">CORE PROTOCOL</span>
              </div>
              <ul className="space-y-4">
                {['Genesis Log Cataloging', 'Knowledge Graph Synthesis', 'Value Engine Projection', 'Pitch Deck Automation'].map(item => (
                  <li key={item} className="flex items-center gap-3 text-stone-400">
                    <CheckCircle2 size={16} className="text-amber-600" />
                    <span className="text-sm font-medium">{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Opportunity Synthesis",
      content: (
        <div className="space-y-8">
          <div className="flex gap-4 mb-8">
            {propositions.map(p => (
              <button 
                key={p.id} 
                onClick={() => setSelectedProposition(p)}
                className={`flex-1 p-4 rounded-xl border transition-all text-left ${selectedProposition.id === p.id ? 'bg-amber-600/10 border-amber-600 text-amber-500' : 'bg-stone-900 border-stone-800 text-stone-500 hover:border-stone-700'}`}
              >
                <div className="text-[10px] font-bold uppercase mb-1">{p.type}</div>
                <div className="text-sm font-bold truncate">{p.title}</div>
              </button>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-12 bg-stone-950 p-8 rounded-3xl border border-stone-800 animate-in fade-in duration-500">
            <div className="space-y-6">
              <div>
                <div className="text-[10px] font-bold text-stone-500 uppercase mb-2">The Challenge</div>
                <p className="text-lg text-stone-300 leading-snug font-cinzel">{selectedProposition.problem}</p>
              </div>
              <div>
                <div className="text-[10px] font-bold text-stone-500 uppercase mb-2">The Alexandria Solution</div>
                <p className="text-sm text-stone-400 leading-relaxed">{selectedProposition.solution}</p>
              </div>
            </div>
            <div className="space-y-6 bg-stone-900/50 p-6 rounded-2xl border border-stone-800">
              <div className="flex justify-between items-end border-b border-stone-800 pb-4">
                <div>
                  <div className="text-[10px] font-bold text-stone-500 uppercase">Valuation Tier</div>
                  <div className="text-2xl font-bold text-amber-500">{selectedProposition.pricing}</div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-bold text-stone-500 uppercase">Est. ROI</div>
                  <div className="text-xl font-bold text-green-500">{selectedProposition.estimatedROI}</div>
                </div>
              </div>
              <ul className="space-y-2">
                <div className="text-[10px] font-bold text-stone-500 uppercase mb-2">Deliverable Pipeline</div>
                {selectedProposition.deliverables.map(d => (
                  <li key={d} className="text-xs text-stone-400 flex items-center gap-2">
                    <Zap size={12} className="text-amber-600" /> {d}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "Strategic Partnerships",
      content: (
        <div className="grid grid-cols-2 gap-12">
          <div className="space-y-6">
            <p className="text-xl text-stone-300 font-cinzel leading-relaxed">
              Identifying and matching with high-tier funding bodies focused on <span className="text-amber-500">Disruptive AI</span> and <span className="text-amber-500">Automation</span>.
            </p>
            <div className="space-y-4">
              {funders.map(f => (
                <div key={f.id} className="p-4 bg-stone-950 border border-stone-800 rounded-xl flex items-center justify-between group hover:border-amber-600/30 transition-all">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-stone-200">{f.name}</span>
                      <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-stone-800 text-stone-500 uppercase">{f.tier}</span>
                    </div>
                    <div className="text-[10px] text-stone-500 mt-1">{f.focus.join(' • ')}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-amber-500">{f.matchScore}% Match</div>
                    <div className="text-[9px] text-stone-600 uppercase font-bold">Signal Score</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="bg-stone-900 border border-stone-800 rounded-3xl p-8 relative overflow-hidden flex flex-col justify-center">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Award size={160} />
            </div>
            <h3 className="text-2xl font-cinzel font-bold mb-4 text-amber-500">Investor Readiness</h3>
            <p className="text-sm text-stone-400 mb-8 leading-relaxed">
              Our automated synthesis pipeline ensures every proposition is backed by real archival assets, market validation data, and executable roadmaps. We reduce the "Time-to-Trust" for institutional funders.
            </p>
            <button className="flex items-center gap-3 bg-stone-100 text-stone-950 px-6 py-3 rounded-xl font-bold uppercase text-xs hover:bg-white transition-all shadow-xl shadow-stone-900/50">
              <ExternalLink size={16} /> Data Room Access
            </button>
          </div>
        </div>
      )
    }
  ];

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-12 pb-24 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      <div className="flex justify-between items-end no-print">
        <div>
          <h1 className="text-4xl font-cinzel font-bold text-stone-100 mb-2">Investor Presentation</h1>
          <p className="text-stone-500 text-sm italic">High-fidelity visualization for venture orchestration.</p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setCurrentSlide(prev => Math.max(0, prev - 1))}
            className="p-3 bg-stone-900 border border-stone-800 rounded-xl text-stone-400 hover:text-stone-100 disabled:opacity-30"
            disabled={currentSlide === 0}
          >
            <ChevronLeft size={24} />
          </button>
          <button 
            onClick={() => setCurrentSlide(prev => Math.min(slides.length - 1, prev + 1))}
            className="p-3 bg-stone-900 border border-stone-800 rounded-xl text-stone-400 hover:text-stone-100 disabled:opacity-30"
            disabled={currentSlide === slides.length - 1}
          >
            <ChevronRight size={24} />
          </button>
          <button 
            onClick={handlePrint}
            className="flex items-center gap-2 bg-amber-600 text-stone-950 px-6 py-3 rounded-xl font-bold uppercase text-xs hover:bg-amber-500 transition-all shadow-lg"
          >
            <FileDown size={18} /> Export PDF Pitch Deck
          </button>
        </div>
      </div>

      <div className="print-content">
        <Slide 
          title={slides[currentSlide].title} 
          index={currentSlide} 
          total={slides.length}
        >
          {slides[currentSlide].content}
        </Slide>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 no-print">
        <div className="p-6 bg-stone-900 border border-stone-800 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-amber-600/10 rounded-xl"><Monitor className="text-amber-500" size={24} /></div>
          <div>
            <div className="text-xl font-bold text-stone-200">Live Deck</div>
            <div className="text-[10px] font-bold text-stone-500 uppercase tracking-widest">Interactive Synthesis</div>
          </div>
        </div>
        <div className="p-6 bg-stone-900 border border-stone-800 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-green-600/10 rounded-xl"><CheckCircle2 className="text-green-500" size={24} /></div>
          <div>
            <div className="text-xl font-bold text-stone-200">Verified</div>
            <div className="text-[10px] font-bold text-stone-500 uppercase tracking-widest">Asset Backed Logic</div>
          </div>
        </div>
        <div className="p-6 bg-stone-900 border border-stone-800 rounded-2xl flex items-center gap-4">
          <div className="p-3 bg-blue-600/10 rounded-xl"><Globe className="text-blue-500" size={24} /></div>
          <div>
            <div className="text-xl font-bold text-stone-200">Global</div>
            <div className="text-[10px] font-bold text-stone-500 uppercase tracking-widest">Search Grounded Intelligence</div>
          </div>
        </div>
      </div>

      <style>{`
        @media print {
          body * { visibility: hidden; }
          .print-content, .print-content * { visibility: visible; }
          .print-content { position: absolute; left: 0; top: 0; width: 100%; }
          .no-print { display: none !important; }
          .presentation-slide { border: none !important; box-shadow: none !important; min-height: 100vh !important; border-radius: 0 !important; }
        }
      `}</style>
    </div>
  );
};

// --- AI Chatbot Component (Enhanced with Search Grounding) ---

const IntelligenceAI = ({ log }: { log: GenesisEntry[] }) => {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, links?: any[] }[]>([
    { role: 'assistant', content: "Protocol Alexandria initialized. Search grounding enabled for market validation. How can I assist you today?" }
  ]);
  const [input, setInput] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [agentMode, setAgentMode] = useState<'Strategist' | 'Archivist' | 'Data Scientist'>('Strategist');
  const [useMarketSearch, setUseMarketSearch] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isThinking]);

  const handleSend = async () => {
    if (!input.trim() || isThinking) return;
    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsThinking(true);

    try {
      const context = [
        `Alexandria Protocol mode: ${agentMode}.`,
        `Market research preference: ${useMarketSearch ? 'enabled' : 'disabled'}.`,
        `Archive snapshot: ${JSON.stringify(log.map(f => ({ name: f.name, collection: f.collection, description: f.description })))}.`
      ].join(' ');

      const history = [...messages, { role: 'user', content: userMessage }]
        .slice(-6)
        .map((item) => ({
          role: item.role,
          content: item.content,
        }));

      const response = await postJson<AlexandriaChatResponse>('/api/ai/alexandria', {
        message: userMessage,
        context,
        history,
      });

      const reply = response.reply || "Synthesis failed.";
      setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: "Failure: Connection to prime directive interrupted." }]);
    } finally {
      setIsThinking(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-16rem)] max-w-4xl mx-auto bg-stone-900 border border-stone-800 rounded-2xl overflow-hidden shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="p-4 bg-stone-950 border-b border-stone-800 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-amber-600/10 rounded-lg"><Sparkles className="text-amber-500" size={20} /></div>
          <div>
            <div className="text-sm font-cinzel font-bold text-stone-100 uppercase tracking-widest">Protocol Intelligence</div>
            <div className="text-[10px] font-mono text-stone-500">{agentMode.toUpperCase()} MODE</div>
          </div>
        </div>
        <div className="flex gap-2 items-center">
          <button 
            onClick={() => setUseMarketSearch(!useMarketSearch)}
            className={`flex items-center gap-1.5 px-3 py-1 text-[9px] font-bold uppercase rounded-full border transition-all ${useMarketSearch ? 'bg-blue-600/20 border-blue-500 text-blue-400' : 'bg-stone-800 border-stone-700 text-stone-500'}`}
          >
            <Globe size={12} /> {useMarketSearch ? 'Market Search ON' : 'Market Search OFF'}
          </button>
          {['Strategist', 'Archivist', 'Data Scientist'].map(m => (
            <button key={m} onClick={() => setAgentMode(m as any)} className={`px-2 py-1 text-[9px] font-bold uppercase rounded border transition-all ${agentMode === m ? 'bg-amber-600 border-amber-500 text-stone-950' : 'bg-stone-800 border-stone-700 text-stone-500 hover:text-stone-300'}`}>
              {m}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-[radial-gradient(circle_at_top_right,rgba(41,37,36,0.3),transparent)]">
        {messages.map((m, i) => (
          <div key={i} className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in duration-300`}>
            <div className={`max-w-[85%] p-4 rounded-2xl text-sm ${m.role === 'user' ? 'bg-amber-600 text-stone-950 font-medium' : 'bg-stone-800 text-stone-200 border border-stone-700'}`}>
              {m.content}
            </div>
            {m.links && m.links.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {m.links.map((link, idx) => (
                  link.web && (
                    <a key={idx} href={link.web.uri} target="_blank" rel="noopener noreferrer" className="text-[10px] bg-stone-950 px-2 py-1 rounded border border-stone-800 text-blue-400 hover:text-blue-300 transition-colors">
                      {link.web.title || 'Source'}
                    </a>
                  )
                ))}
              </div>
            )}
          </div>
        ))}
        {isThinking && <div className="text-xs font-mono text-stone-500 animate-pulse flex items-center gap-2"><Loader2 className="animate-spin" size={14} /> Synthesizing live market intelligence...</div>}
        <div ref={chatEndRef} />
      </div>
      <div className="p-4 bg-stone-950 border-t border-stone-800">
        <div className="flex items-center gap-2">
          <input type="text" value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleSend()} placeholder="Validate archive monetization strategy..." className="flex-1 bg-stone-900 border border-stone-800 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-amber-600/50" />
          <button onClick={handleSend} disabled={isThinking} className="bg-amber-600 p-3 rounded-xl"><Send size={18} /></button>
        </div>
      </div>
    </div>
  );
};

// --- Strategic Timeline (Roadmap) Component ---

const RoadmapView = ({ propositions }: { propositions: Proposition[] }) => {
  return (
    <div className="bg-stone-900 rounded-xl border border-stone-800 p-8 shadow-2xl">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-cinzel font-bold">Strategic Commercialization Roadmap</h2>
          <p className="text-xs text-stone-500 uppercase tracking-widest mt-1">Multi-Quarter Execution Timeline</p>
        </div>
        <div className="flex items-center gap-2 text-stone-500 text-[10px] font-bold uppercase">
          <Calendar size={14} /> Q2 2025 Focus
        </div>
      </div>
      
      <div className="relative pt-10">
        {/* Quarter markers */}
        <div className="absolute top-0 w-full flex text-[9px] font-bold text-stone-600 border-b border-stone-800 pb-2">
          <div className="flex-1 text-center">APRIL</div>
          <div className="flex-1 text-center border-l border-stone-800">MAY</div>
          <div className="flex-1 text-center border-l border-stone-800">JUNE</div>
          <div className="flex-1 text-center border-l border-stone-800">JULY</div>
        </div>
        
        <div className="space-y-6 mt-4">
          {propositions.map((p, i) => (
            <div key={p.id} className="group">
              <div className="flex justify-between text-[11px] mb-2 px-2">
                <span className="font-bold text-stone-300 group-hover:text-amber-500 transition-colors">{p.title}</span>
                <span className="text-stone-600 font-mono italic">{p.pricing}</span>
              </div>
              <div className="w-full bg-stone-950 h-3 rounded-full relative overflow-hidden border border-stone-800 shadow-inner">
                {/* Visualizing dates roughly (0% = April 1, 100% = July 31) */}
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${i % 2 === 0 ? 'bg-amber-600 shadow-[0_0_10px_rgba(217,119,6,0.3)]' : 'bg-blue-600 shadow-[0_0_10px_rgba(37,99,235,0.3)]'}`}
                  style={{ 
                    marginLeft: `${(new Date(p.startDate).getTime() - new Date('2025-04-01').getTime()) / (new Date('2025-08-01').getTime() - new Date('2025-04-01').getTime()) * 100}%`,
                    width: `${(new Date(p.endDate).getTime() - new Date(p.startDate).getTime()) / (new Date('2025-08-01').getTime() - new Date('2025-04-01').getTime()) * 100}%`
                  }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// --- Asset Views ---

const AssetPreview = ({ asset }: { asset: GenesisEntry }) => {
  const isImage = ['PNG', 'JPG', 'JPEG', 'FIGMA', 'IMAGE'].some(t => asset.type.toUpperCase().includes(t));
  const isDoc = ['PDF', 'TXT', 'DOC', 'CSV', 'JSON', 'JS', 'PY', 'CODE'].some(t => asset.type.toUpperCase().includes(t));

  return (
    <div className="w-full bg-stone-950 rounded-lg border border-stone-800 overflow-hidden min-h-[160px] flex items-center justify-center relative">
      {isImage && asset.previewUrl ? (
        <img src={asset.previewUrl} alt={asset.name} className="w-full h-full object-cover opacity-80" />
      ) : isDoc && asset.contentSnippet ? (
        <div className="w-full h-full p-4 font-mono text-[10px] text-stone-400 overflow-hidden whitespace-pre-wrap">
          {asset.contentSnippet}
          <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-stone-950 to-transparent"></div>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-2 text-stone-600">
          {isImage ? <ImageIcon size={32} /> : isDoc ? <FileText size={32} /> : <Layers size={32} />}
          <span className="text-[10px] font-bold uppercase tracking-widest">Preview Unavailable</span>
        </div>
      )}
      <div className="absolute top-2 right-2 px-2 py-1 bg-stone-900/80 backdrop-blur rounded text-[9px] font-bold text-stone-500 uppercase border border-stone-800">
        {asset.type}
      </div>
    </div>
  );
};

const Dashboard = ({ log, propositions }: { log: GenesisEntry[], propositions: Proposition[] }) => {
  const portfolioValue = propositions.length * 25000;
  
  return (
    <div className="space-y-6 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-cinzel font-bold text-stone-100 mb-1">Commercial Portfolio Dashboard</h1>
          <p className="text-stone-500 text-sm italic">Synthesis of archival value and execution feasibility.</p>
        </div>
        <div className="flex gap-4">
          <div className="bg-stone-900 border border-stone-800 p-4 rounded-lg flex flex-col items-center shadow-xl">
            <span className="text-xl font-bold text-amber-500">${portfolioValue.toLocaleString()}</span>
            <span className="text-[10px] uppercase text-stone-500 font-bold tracking-widest">Aggregate Value</span>
          </div>
          <div className="bg-stone-900 border border-stone-800 p-4 rounded-lg flex flex-col items-center shadow-xl">
            <span className="text-xl font-bold text-green-500">{Math.round(propositions.reduce((a,b)=>a+b.feasibility,0)/propositions.length)}%</span>
            <span className="text-[10px] uppercase text-stone-500 font-bold tracking-widest">Avg Feasibility</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-stone-900 rounded-xl border border-stone-800 p-6 shadow-2xl">
          <h3 className="text-lg font-cinzel font-bold mb-6 flex items-center gap-2">
            <TrendingUp size={20} className="text-amber-500" /> Revenue Synthesis Projection
          </h3>
          <div className="space-y-4">
            {propositions.map(p => (
              <div key={p.id} className="p-4 bg-stone-950 border border-stone-800 rounded-lg hover:border-amber-600/30 transition-all flex items-center justify-between group">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm font-bold text-stone-200">{p.title}</span>
                    <span className={`px-1.5 py-0.5 rounded-[4px] text-[8px] font-bold uppercase ${p.type === 'Consultancy' ? 'bg-purple-900/30 text-purple-400' : p.type === 'Digital Product' ? 'bg-blue-900/30 text-blue-400' : 'bg-green-900/30 text-green-400'}`}>{p.type}</span>
                  </div>
                  <div className="w-48 h-1.5 bg-stone-900 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-600 group-hover:bg-amber-500 transition-colors" style={{ width: `${p.feasibility}%` }}></div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-[10px] font-mono text-amber-500 font-bold">{p.estimatedROI} ROI</div>
                  <div className="text-[10px] font-mono text-stone-500">{p.pricing}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-stone-900 rounded-xl border border-stone-800 p-6 flex flex-col shadow-2xl">
          <h3 className="text-lg font-cinzel font-bold mb-4 flex items-center gap-2">
            <Shield size={20} className="text-amber-500" /> Strategic Integrity
          </h3>
          <div className="space-y-4 flex-1">
            <div className="p-3 bg-green-600/10 border border-green-600/20 rounded-lg flex items-center gap-3">
              <CheckCircle2 className="text-green-500" size={18} />
              <div>
                <div className="text-[10px] font-bold text-green-400 uppercase">Archive Cleanliness</div>
                <div className="text-xs text-stone-400">92% Compliance Rating</div>
              </div>
            </div>
            <div className="p-3 bg-amber-600/10 border border-amber-600/20 rounded-lg flex items-center gap-3">
              <AlertTriangle className="text-amber-500" size={18} />
              <div>
                <div className="text-[10px] font-bold text-amber-400 uppercase">Attention Required</div>
                <div className="text-xs text-stone-400">"f5" Risk Level HIGH (Legal)</div>
              </div>
            </div>
          </div>
          <div className="mt-6 pt-6 border-t border-stone-800">
             <button onClick={() => alert('Compiling Protocol Whitepaper...')} className="w-full py-3 bg-amber-600 text-stone-950 rounded-lg font-bold text-xs uppercase flex items-center justify-center gap-2 hover:bg-amber-500 transition-all shadow-lg shadow-amber-900/20">
              <FileDown size={16} /> Compile Archive Whitepaper
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Knowledge Network Component ---

const KnowledgeGraph = ({ graphNodes, graphLinks }: { graphNodes: GraphNode[], graphLinks: GraphLink[] }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    d3.select(containerRef.current).selectAll("*").remove();
    const width = containerRef.current.clientWidth;
    const height = 500;
    const svg = d3.select(containerRef.current).append("svg").attr("width", width).attr("height", height).attr("class", "bg-stone-950 rounded-xl border border-stone-800 overflow-hidden cursor-move shadow-inner");
    const g = svg.append("g");
    const zoom = d3.zoom().scaleExtent([0.1, 8]).on("zoom", (event: any) => g.attr("transform", event.transform));
    svg.call(zoom as any);

    const simulation = d3.forceSimulation(graphNodes as any).force("link", d3.forceLink(graphLinks as any).id((d: any) => d.id).distance(100)).force("charge", d3.forceManyBody().strength(-300)).force("center", d3.forceCenter(width / 2, height / 2));
    const link = g.append("g").attr("stroke", "#444").attr("stroke-opacity", 0.4).selectAll("line").data(graphLinks).join("line").attr("stroke-width", 1);
    const node = g.append("g").selectAll("g").data(graphNodes).join("g").attr("class", "cursor-pointer").on("click", (event: any, d: any) => setSelectedNode(d)).call(d3.drag().on("start", (e: any) => { if (!e.active) simulation.alphaTarget(0.3).restart(); e.subject.fx = e.subject.x; e.subject.fy = e.subject.y; }).on("drag", (e: any) => { e.subject.fx = e.x; e.subject.fy = e.y; }).on("end", (e: any) => { if (!e.active) simulation.alphaTarget(0); e.subject.fx = null; e.subject.fy = null; }) as any);

    node.append("circle").attr("r", (d: any) => d.type === 'concept' ? 14 : 10).attr("fill", (d: any) => d.type === 'concept' ? "#d97706" : d.type === 'file' ? "#78716c" : "#2563eb").attr("stroke", (d: any) => selectedNode?.id === d.id ? "#fff" : "#1c1917").attr("stroke-width", 2);
    node.append("text").text((d: any) => d.label).attr("x", 15).attr("y", 4).attr("fill", "#a8a29e").style("font-size", "10px").style("font-family", "JetBrains Mono").style("pointer-events", "none");

    simulation.on("tick", () => { link.attr("x1", (d: any) => d.source.x).attr("y1", (d: any) => d.source.y).attr("x2", (d: any) => d.target.x).attr("y2", (d: any) => d.target.y); node.attr("transform", (d: any) => `translate(${d.x},${d.y})`); });
  }, [graphNodes, graphLinks, selectedNode]);

  return (
    <div className="flex gap-6 h-[500px]">
      <div ref={containerRef} className="flex-1 relative"></div>
      {selectedNode && (
        <div className="w-80 bg-stone-900 border border-stone-800 rounded-xl p-6 flex flex-col animate-in slide-in-from-right-4 duration-300 shadow-2xl">
          <div className="flex justify-between items-start mb-4">
            <div className="text-[10px] font-bold text-amber-500 uppercase tracking-widest">{selectedNode.type}</div>
            <button onClick={() => setSelectedNode(null)} className="text-stone-500 hover:text-stone-300 transition-colors">×</button>
          </div>
          <h4 className="text-xl font-cinzel font-bold mb-2">{selectedNode.label}</h4>
          <div className="text-xs text-stone-400 mb-6 font-mono">NODE_UID: {selectedNode.id}</div>
          <div className="flex-1 space-y-4 overflow-y-auto">
            <div className="p-3 bg-stone-950 rounded-lg border border-stone-800">
              <div className="text-[9px] font-bold text-stone-500 uppercase mb-1">Semantic Connections</div>
              <div className="text-xs text-stone-300">Linked to 3 high-value clusters.</div>
            </div>
          </div>
          <button className="mt-4 w-full py-2 bg-stone-100 text-stone-950 rounded font-bold text-[10px] uppercase hover:bg-white transition-all">Synthesize Outcomes</button>
        </div>
      )}
    </div>
  );
};

const OperationsHub = ({ kpiPayload, kpiError }: { kpiPayload: any, kpiError: string | null }) => {
  const kpis = Array.isArray(kpiPayload?.kpis) ? kpiPayload.kpis.slice(0, 6) : [];
  const summary = kpiPayload?.summary;

  const statusClass = (status: string) => {
    if (status === 'on_track') return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/30';
    if (status === 'at_risk') return 'bg-amber-500/10 text-amber-500 border-amber-500/30';
    if (status === 'off_track') return 'bg-rose-500/10 text-rose-500 border-rose-500/30';
    return 'bg-stone-900 text-stone-400 border-stone-800';
  };

  return (
    <div className="space-y-10 animate-in fade-in slide-in-from-bottom-6 duration-700">
      <div className="bg-stone-900 border border-stone-800 rounded-2xl p-8 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-[10px] uppercase tracking-[0.3em] text-stone-500 font-mono">Operations Command</div>
            <h2 className="text-3xl font-cinzel font-bold text-amber-500">Culture + KPI Execution Stack</h2>
          </div>
          <div className="px-3 py-1 text-[10px] uppercase font-bold tracking-widest rounded-full border border-amber-600/40 text-amber-500">
            Live
          </div>
        </div>

        {kpiError && (
          <div className="p-4 rounded-lg border border-stone-800 text-stone-400 text-sm">
            KPI feed offline: {kpiError}
          </div>
        )}

        {summary && (
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
            {['on_track', 'at_risk', 'off_track', 'unknown'].map((key) => (
              <div key={key} className="p-3 rounded-lg border border-stone-800 bg-stone-950">
                <div className="text-[9px] uppercase tracking-widest text-stone-500">{key.replace('_', ' ')}</div>
                <div className="text-xl font-bold text-stone-100">{summary[key]}</div>
              </div>
            ))}
            <div className="p-3 rounded-lg border border-stone-800 bg-stone-950">
              <div className="text-[9px] uppercase tracking-widest text-stone-500">total</div>
              <div className="text-xl font-bold text-stone-100">{summary.total}</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {kpis.map((kpi: any) => (
            <div key={kpi.id} className="p-4 rounded-xl border border-stone-800 bg-stone-950">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-stone-200">{kpi.name}</div>
                  <div className="text-[10px] text-stone-500 uppercase tracking-widest">{kpi.category} • {kpi.owner || 'Owner TBD'}</div>
                </div>
                <span className={`text-[9px] px-2 py-1 rounded-full border ${statusClass(kpi.status)}`}>
                  {kpi.status_label}
                </span>
              </div>
              <div className="mt-3 text-xs text-stone-400">
                Target: {kpi.target} {kpi.unit} • Actual: {kpi.actual ?? 'n/a'} {kpi.unit}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-stone-900 border border-stone-800 rounded-2xl p-6">
          <div className="text-[10px] uppercase tracking-[0.3em] text-stone-500 font-mono mb-4">Operating Docs</div>
          <div className="space-y-3">
            {OPERATIONS_DOCS.map((doc) => (
              <div key={doc.path} className="flex items-center justify-between border border-stone-800 rounded-lg px-4 py-3 bg-stone-950">
                <div>
                  <div className="text-sm text-stone-200 font-semibold">{doc.label}</div>
                  <div className="text-[10px] text-stone-500 font-mono">{doc.path}</div>
                </div>
                <FileText size={16} className="text-amber-500" />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-stone-900 border border-stone-800 rounded-2xl p-6">
          <div className="text-[10px] uppercase tracking-[0.3em] text-stone-500 font-mono mb-4">Live Services</div>
          <div className="space-y-3">
            {LIVE_SERVICES.map((svc) => (
              <a key={svc.url} href={svc.url} target="_blank" rel="noreferrer" className="flex items-center justify-between border border-stone-800 rounded-lg px-4 py-3 bg-stone-950 hover:border-amber-600/50 transition-all">
                <div>
                  <div className="text-sm text-stone-200 font-semibold">{svc.label}</div>
                  <div className="text-[10px] text-stone-500 font-mono">{svc.url}</div>
                </div>
                <ExternalLink size={16} className="text-amber-500" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Main App Shell ---

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [log, setLog] = useState<GenesisEntry[]>(INITIAL_GENESIS_LOG);
  const [selectedAsset, setSelectedAsset] = useState<GenesisEntry | null>(null);
  const [propositions] = useState<Proposition[]>(INITIAL_PROPOSITIONS);
  const [graphNodes] = useState<GraphNode[]>(GRAPH_DATA.nodes);
  const [graphLinks] = useState<GraphLink[]>(GRAPH_DATA.links);
  const [consoleLogs, setConsoleLogs] = useState([{ type: 'success', text: 'Protocol Alexandria Prime Online. Multi-Agent Synthesis Active.' }]);
  const [kpiPayload, setKpiPayload] = useState<any>(null);
  const [kpiError, setKpiError] = useState<string | null>(null);

  const addLog = (type: string, text: string) => setConsoleLogs(prev => [...prev.slice(-10), { type, text }]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let isMounted = true;
    fetchKpiTargets()
      .then((data) => {
        if (isMounted) {
          setKpiPayload(data);
        }
      })
      .catch(() => {
        if (isMounted) {
          setKpiError('Awaiting KPI telemetry sync.');
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach(file => {
      const id = `f${log.length + 1}`;
      const type = file.name.split('.').pop()?.toUpperCase() || 'UNKNOWN';
      
      const reader = new FileReader();
      reader.onload = (event) => {
        const result = event.target?.result as string;
        const isImg = ['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP'].includes(type);
        
        const newEntry: GenesisEntry = {
          id,
          name: file.name,
          type,
          size: `${(file.size / 1024).toFixed(1)} KB`,
          date: new Date().toISOString().split('T')[0],
          status: FileStatus.TRIAGE,
          tags: ['ingested', type.toLowerCase()],
          collection: 'Direct Ingestion Queue',
          copyright: 'Unknown',
          potentialUse: PotentialUse.LEARNING,
          description: `User-uploaded asset: ${file.name}`,
          confidenceScore: 0,
          previewUrl: isImg ? result : undefined,
          contentSnippet: !isImg ? result.slice(0, 300) + '...' : undefined,
          riskLevel: RiskLevel.MEDIUM
        };

        setLog(prev => [...prev, newEntry]);
        addLog('info', `Ingesting and Auditing: ${file.name}`);
      };

      if (['PNG', 'JPG', 'JPEG', 'GIF', 'WEBP'].includes(type)) {
        reader.readAsDataURL(file);
      } else {
        reader.readAsText(file);
      }
    });
  };

  const handlePitchDeck = async (p: Proposition) => {
    addLog('ai', `Synthesizing professional pitch deck for: ${p.title}`);
    setActiveTab('presentation');
  };

  return (
    <div className="flex h-screen bg-stone-950 text-stone-200 overflow-hidden font-inter selection:bg-amber-600 selection:text-white">
      <input type="file" ref={fileInputRef} className="hidden" multiple onChange={handleFileUpload} />
      
      <aside className="w-64 bg-[#1c1917] border-r border-stone-800 flex flex-col p-6 space-y-8 z-20 shadow-2xl no-print">
        <div className="flex items-center gap-3 cursor-pointer group" onClick={() => setActiveTab('dashboard')}>
          <div className="bg-amber-600 p-2 rounded-lg group-hover:scale-105 transition-transform"><Library size={24} className="text-stone-950" /></div>
          <div>
            <div className="text-xl font-cinzel font-bold tracking-tighter">ALEXANDRIA</div>
            <div className="text-[9px] font-mono font-bold text-stone-500 uppercase tracking-widest">Global Asset Hub</div>
          </div>
        </div>
        <nav className="flex-1 space-y-1.5">
          <SidebarItem active={activeTab === 'dashboard'} icon={Activity} label="Strategic Hub" onClick={() => setActiveTab('dashboard')} />
          <SidebarItem active={activeTab === 'intelligence'} icon={Sparkles} label="Market Intelligence" onClick={() => setActiveTab('intelligence')} />
          <SidebarItem active={activeTab === 'genesis'} icon={Database} label="Genesis Archive" onClick={() => setActiveTab('genesis')} />
          <SidebarItem active={activeTab === 'graph'} icon={Network} label="Knowledge Map" onClick={() => setActiveTab('graph')} />
          <SidebarItem active={activeTab === 'roadmap'} icon={Layers} label="Strategic Roadmap" onClick={() => setActiveTab('roadmap')} />
          <SidebarItem active={activeTab === 'operations'} icon={Monitor} label="Ops Command" onClick={() => setActiveTab('operations')} />
          <SidebarItem active={activeTab === 'value'} icon={TrendingUp} label="Value Engine" onClick={() => setActiveTab('value')} />
          <SidebarItem active={activeTab === 'presentation'} icon={Presentation} label="Investor Deck" onClick={() => setActiveTab('presentation')} />
        </nav>
        <div className="p-4 bg-stone-900/50 rounded-xl border border-stone-800">
          <div className="text-[10px] text-stone-500 font-mono mb-2 uppercase tracking-tighter">Asset Liquidity</div>
          <div className="w-full bg-stone-950 h-1.5 rounded-full overflow-hidden shadow-inner">
            <div className="bg-amber-600 w-3/4 h-full animate-pulse"></div>
          </div>
          <div className="flex justify-between mt-2 text-[8px] font-bold text-stone-600 uppercase">
            <span>Portfolio Sync</span>
            <span>84%</span>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col relative">
        <header className="h-16 border-b border-stone-800 flex items-center justify-between px-8 bg-[#1c1917]/80 backdrop-blur-xl sticky top-0 z-10 shadow-lg no-print">
          <div className="flex items-center gap-3 text-[10px] font-mono text-stone-400 uppercase tracking-widest">
            <Shield size={14} className="text-amber-700" /> Security: <span className="text-amber-500 font-bold">ALEX_OMEGA_SECURE</span>
          </div>
          <div className="flex gap-3">
            <button onClick={() => fileInputRef.current?.click()} className="flex items-center gap-2 bg-stone-800 px-4 py-2 rounded-lg text-xs font-bold border border-stone-700 hover:bg-stone-700 transition-all"><Upload size={14} /> Batch Ingest</button>
            <button className="flex items-center gap-2 bg-amber-600 px-4 py-2 rounded-lg text-stone-950 text-xs font-bold hover:bg-amber-500 transition-all shadow-lg shadow-amber-600/20"><Rocket size={14} /> Launch Synthesis</button>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-10 custom-scrollbar flex gap-6">
          <div className="flex-1 min-w-0">
            {activeTab === 'dashboard' && <Dashboard log={log} propositions={propositions} />}
            {activeTab === 'intelligence' && <IntelligenceAI log={log} />}
            {activeTab === 'graph' && <KnowledgeGraph graphNodes={graphNodes} graphLinks={graphLinks} />}
            {activeTab === 'roadmap' && <RoadmapView propositions={propositions} />}
            {activeTab === 'operations' && <OperationsHub kpiPayload={kpiPayload} kpiError={kpiError} />}
            {activeTab === 'presentation' && <PresentationView propositions={propositions} funders={POTENTIAL_FUNDERS} />}
            {activeTab === 'genesis' && (
              <div className="bg-stone-900 rounded-xl border border-stone-800 overflow-hidden shadow-2xl">
                <table className="w-full text-left text-sm border-collapse">
                  <thead className="bg-stone-950 text-stone-500 uppercase text-[9px] font-bold tracking-widest sticky top-0 z-10 border-b border-stone-800">
                    <tr>
                      <th className="p-4 w-12 text-center">Preview</th>
                      <th className="p-4">Identity</th>
                      <th className="p-4">Risk Audit</th>
                      <th className="p-4">Potential</th>
                      <th className="p-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-800">
                    {log.map(item => (
                      <tr 
                        key={item.id} 
                        className={`hover:bg-stone-800/50 transition-colors cursor-pointer group ${selectedAsset?.id === item.id ? 'bg-amber-600/10' : ''}`}
                        onClick={() => setSelectedAsset(item)}
                      >
                        <td className="p-4 flex justify-center">
                          <div className="w-8 h-8 rounded bg-stone-950 border border-stone-800 flex items-center justify-center text-stone-600 overflow-hidden group-hover:border-amber-600/50 transition-all shadow-inner">
                            {item.previewUrl ? <img src={item.previewUrl} alt="" className="w-full h-full object-cover" /> : <FileText size={14} />}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="font-bold text-stone-200 text-xs">{item.name}</div>
                          <div className="text-[10px] text-stone-500 font-mono">{item.id} • {item.size}</div>
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-0.5 rounded-[4px] text-[8px] font-bold uppercase flex items-center gap-1 w-fit border ${
                            item.riskLevel === RiskLevel.LOW ? 'bg-green-900/20 border-green-900/50 text-green-500' : 
                            item.riskLevel === RiskLevel.MEDIUM ? 'bg-amber-900/20 border-amber-900/50 text-amber-500' : 
                            'bg-red-900/20 border-red-900/50 text-red-500'
                          }`}>
                            <div className={`h-1 w-1 rounded-full ${item.riskLevel === RiskLevel.LOW ? 'bg-green-500' : item.riskLevel === RiskLevel.MEDIUM ? 'bg-amber-500' : 'bg-red-500'}`}></div>
                            {item.riskLevel} Risk
                          </span>
                        </td>
                        <td className="p-4 text-xs text-stone-400 font-medium italic">
                          {item.potentialUse}
                        </td>
                        <td className="p-4">
                          <span className={`px-2 py-1 rounded text-[9px] uppercase font-bold border ${
                            item.status === FileStatus.ANALYZED ? 'bg-green-600/10 border-green-600/20 text-green-500' :
                            item.status === FileStatus.TRIAGE ? 'bg-blue-600/10 border-blue-600/20 text-blue-500' :
                            'bg-stone-800 border-stone-700 text-stone-500'
                          }`}>
                            {item.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {activeTab === 'value' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {propositions.map(p => (
                  <div key={p.id} className="bg-stone-900 border border-stone-800 rounded-xl overflow-hidden hover:border-amber-600/50 transition-all group flex flex-col shadow-2xl">
                    <div className="p-4 bg-stone-950 border-b border-stone-800 flex justify-between items-center">
                      <span className="text-[10px] font-bold text-amber-500 uppercase tracking-widest">{p.type}</span>
                      <div className="flex items-center gap-1.5 text-[10px] font-mono text-stone-500">
                        <Calendar size={12} /> {new Date(p.startDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </div>
                    </div>
                    <div className="p-6 flex-1">
                      <h4 className="text-lg font-cinzel font-bold mb-3 group-hover:text-amber-500 transition-colors leading-tight">{p.title}</h4>
                      <p className="text-xs text-stone-400 mb-6 line-clamp-3 leading-relaxed">{p.problem}</p>
                      
                      <div className="flex justify-between items-center mb-6">
                        <div className="text-sm font-bold text-stone-100">{p.pricing}</div>
                        <div className="flex items-center gap-1.5 text-green-500 font-bold text-[10px] uppercase">
                          <TrendingUp size={14} /> {p.estimatedROI}
                        </div>
                      </div>
                      
                      <button 
                        onClick={() => handlePitchDeck(p)}
                        className="w-full py-2.5 bg-stone-100 text-stone-950 rounded-lg font-bold text-[10px] uppercase flex items-center justify-center gap-2 hover:bg-white transition-all shadow-lg"
                      >
                        <Rocket size={14} /> View Investor Deck
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Asset Side Inspector */}
          {selectedAsset && activeTab === 'genesis' && (
            <div className="w-96 bg-stone-900 border border-stone-800 rounded-xl flex flex-col shadow-2xl animate-in slide-in-from-right-4 duration-300 no-print">
              <div className="p-4 border-b border-stone-800 flex justify-between items-center bg-stone-950/50 rounded-t-xl">
                <div className="text-[10px] font-bold text-amber-500 uppercase tracking-[0.2em]">Asset Intelligence</div>
                <button onClick={() => setSelectedAsset(null)} className="p-1 hover:bg-stone-800 rounded text-stone-500 transition-colors">
                  <X size={18} />
                </button>
              </div>
              
              <div className="p-6 space-y-6 overflow-y-auto custom-scrollbar">
                <AssetPreview asset={selectedAsset} />

                <div>
                  <h4 className="text-xl font-cinzel font-bold text-stone-100 break-words">{selectedAsset.name}</h4>
                  <p className="text-xs text-stone-500 font-mono mt-1 uppercase tracking-tighter">STRUCTURAL_ID: {selectedAsset.id}</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className={`p-3 rounded border ${selectedAsset.riskLevel === RiskLevel.HIGH ? 'bg-red-950/20 border-red-900/50' : 'bg-stone-950 border-stone-800'}`}>
                    <div className="text-[9px] font-bold text-stone-600 uppercase mb-1">Risk Profile</div>
                    <div className={`text-sm font-bold ${selectedAsset.riskLevel === RiskLevel.HIGH ? 'text-red-500' : 'text-amber-500'}`}>{selectedAsset.riskLevel}</div>
                  </div>
                  <div className="p-3 bg-stone-950 rounded border border-stone-800">
                    <div className="text-[9px] font-bold text-stone-600 uppercase mb-1">Confidence</div>
                    <div className="text-sm font-bold text-stone-300">{selectedAsset.confidenceScore}%</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-stone-500 uppercase">
                    <Tag size={12} /> Strategy Tags
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedAsset.tags.map(t => (
                      <span key={t} className="px-2 py-1 bg-stone-800 text-stone-400 text-[9px] font-bold uppercase rounded border border-stone-700">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-stone-500 uppercase">
                    <Activity size={12} /> Strategic Synthesis
                  </div>
                  <p className="text-xs text-stone-300 leading-relaxed bg-stone-950/50 p-3 rounded border border-stone-800 italic">
                    {selectedAsset.description}
                  </p>
                </div>

                <button className="w-full py-3 bg-amber-600 hover:bg-amber-500 text-stone-950 font-bold text-xs uppercase rounded-lg shadow-xl shadow-amber-600/10 transition-all flex items-center justify-center gap-2">
                  <Zap size={16} /> Monetize Asset
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="h-32 bg-stone-950 border-t border-stone-800 flex flex-col px-6 py-4 relative z-20 no-print">
          <div className="flex items-center gap-2 mb-2">
            <TerminalIcon size={14} className="text-amber-600" />
            <span className="text-[9px] font-bold text-stone-500 uppercase tracking-widest">Global Runtime Logs</span>
            <div className="flex-1 h-px bg-stone-800 mx-4"></div>
          </div>
          <div className="flex-1 overflow-y-auto space-y-1 custom-scrollbar">
            {consoleLogs.map((l, i) => <ConsoleLine key={i} type={l.type} text={l.text} />)}
          </div>
        </div>
      </main>
    </div>
  );
}
