import React, { useState, useRef } from 'react';
import { Terminal, Layers, ShieldCheck, Cpu, Activity, FileText, Sparkles, Upload, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { RoleDossierCard } from '../components/interview/RoleDossierCard';
import { HardwareDiagnosticsConsole } from '../components/interview/HardwareDiagnosticsConsole';
import { useSessionStore } from '../store/sessionStore';
import { extractPdfText } from '../api/client';

interface HomePageProps {
  onStartSession: (roleId: string, interviewType: string, language: string, jdText?: string, resumeText?: string) => void;
  isLoading: boolean;
}

const ROLES = [
  {
    id: 'software_engineer',
    title: 'Software Engineer',
    subheadline: 'Distributed Systems, Concurrency & Low-Latency Architecture',
    description:
      'Evaluates architectural trade-offs, p99 latency guarantees, cache coherence, distributed transactions, and real-time concurrency under load.',
    tags: ['SYSTEM DESIGN', 'CONCURRENCY', 'DISTRIBUTED ALGORITHMS', 'STORAGE ENGINES'],
    benchmark: '85+ (Strong)',
    icon: Terminal,
    iconColor: '#F59E0B',
  },
  {
    id: 'product_manager',
    title: 'Product Manager',
    subheadline: 'Product Sense, Roadmapping & North Star Metric Decomposition',
    description:
      'Evaluates prioritization frameworks (RICE/Kano), metric decomposition, user empathy discovery, and cross-functional conflict resolution.',
    tags: ['PRODUCT SENSE', 'METRIC TAXONOMY', 'GTM EXECUTION', 'STAKEHOLDER ROADMAP'],
    benchmark: '85+ (Strong)',
    icon: Layers,
    iconColor: '#10B981',
  },
  {
    id: 'hr_behavioral',
    title: 'HR & Executive Behavioral',
    subheadline: 'Leadership Principles, Ethical Decision-Making & STAR Framework',
    description:
      'Evaluates Situation-Task-Action-Result narratives, ethical decision-making, executive composure, and navigating high-friction workplace dynamics.',
    tags: ['STAR METHOD', 'EXECUTIVE PRESENCE', 'CONFLICT RESOLUTION', 'ETHICAL GOVERNANCE'],
    benchmark: '85+ (Strong)',
    icon: ShieldCheck,
    iconColor: '#FB7185',
  },
];

/**
 * HomePage Component (Screen 1: The Executive Interview Suite)
 * Studio-grade asymmetric layout avoiding AI-slop:
 * - Left column: Suite designation, commanding Space Grotesk headline, and 3D tilt role dossiers
 * - Right column: Live Hardware Diagnostics Console with camera reticle & real-time mic visualizer
 */
export const HomePage: React.FC<HomePageProps> = ({ onStartSession, isLoading }) => {
  const [selectedRoleId, setSelectedRoleId] = useState<string>('software_engineer');
  const [jdText, setJdText] = useState<string>('');
  const [resumeText, setResumeText] = useState<string>('');

  const jdFileInputRef = useRef<HTMLInputElement>(null);
  const resumeFileInputRef = useRef<HTMLInputElement>(null);
  const [jdUploading, setJdUploading] = useState<boolean>(false);
  const [resumeUploading, setResumeUploading] = useState<boolean>(false);
  const [jdStatus, setJdStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [resumeStatus, setResumeStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const { selectRole } = useSessionStore();

  const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    target: 'jd' | 'resume'
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input value so re-uploading the same file works
    e.target.value = '';

    const setStatus = target === 'jd' ? setJdStatus : setResumeStatus;
    const setUploading = target === 'jd' ? setJdUploading : setResumeUploading;
    const setText = target === 'jd' ? setJdText : setResumeText;

    // 1. Client-side validation: PDF type & 2MB limit
    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      setStatus({ type: 'error', message: 'Only PDF files are accepted.' });
      setTimeout(() => {
        setStatus((prev) => (prev?.type === 'error' && prev.message === 'Only PDF files are accepted.' ? null : prev));
      }, 4000);
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setStatus({ type: 'error', message: 'Max 2 MB' });
      setTimeout(() => {
        setStatus((prev) => (prev?.type === 'error' && prev.message === 'Max 2 MB' ? null : prev));
      }, 4000);
      return;
    }

    // 2. Perform extraction
    setUploading(true);
    setStatus(null);

    try {
      const res = await extractPdfText(file);
      setText(res.text);
      const successMsg = `Extracted (${res.text.length} chars)`;
      setStatus({ type: 'success', message: successMsg });
      setTimeout(() => {
        setStatus((prev) => (prev?.type === 'success' && prev.message === successMsg ? null : prev));
      }, 3000);
    } catch (err: any) {
      const errMsg = err?.message || 'Failed to extract PDF text';
      setStatus({ type: 'error', message: errMsg });
      setTimeout(() => {
        setStatus((prev) => (prev?.type === 'error' && prev.message === errMsg ? null : prev));
      }, 4000);
    } finally {
      setUploading(false);
    }
  };

  const handleSelectRole = (id: string) => {
    setSelectedRoleId(id);
    const selected = ROLES.find((r) => r.id === id);
    if (selected) {
      selectRole(id, selected.title);
    }
  };

  const handleEnterRoom = () => {
    const selected = ROLES.find((r) => r.id === selectedRoleId);
    if (selected) {
      selectRole(selected.id, selected.title);
    }
    onStartSession(selectedRoleId, 'all', 'en', jdText, resumeText);
  };

  const selectedRole = ROLES.find((r) => r.id === selectedRoleId) || ROLES[0];

  return (
    <div className="w-full min-h-[calc(100vh-4rem)] bg-surface-ground py-8 sm:py-12 px-4 sm:px-6 lg:px-8 flex flex-col justify-center">
      <div className="max-w-7xl mx-auto w-full">
        {/* Asymmetric Studio Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
          {/* Left Column: Suite Designation & 3D Tilt Role Dossiers (col-span-7) */}
          <div className="lg:col-span-7 space-y-8">
            {/* Context & Headline (Asymmetric, not centered) */}
            <div className="space-y-3">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-surface-panel border border-border-subtle text-amber-signal text-xs font-mono font-semibold">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-signal animate-pulse" />
                <span>SYSTEM DESIGNATION // FYP 2026</span>
              </div>

              <h1 className="font-display font-bold text-4xl sm:text-5xl lg:text-5xl tracking-tight text-text-primary leading-[1.1]">
                Executive Interview <br />
                <span className="text-amber-signal">Simulation Suite</span>
              </h1>

              <p className="font-body text-text-secondary text-base sm:text-lg leading-relaxed max-w-2xl">
                High-fidelity multimodal interview training. Evaluates technical depth, vocal pacing,
                and physical composure via real-time local vision landmarker and Whisper speech pipeline.
              </p>
            </div>

            {/* Role Dossiers Header */}
            <div className="pt-2">
              <div className="flex items-center justify-between mb-4 border-b border-border-subtle/60 pb-3">
                <h2 className="font-display font-semibold text-base sm:text-lg text-text-primary flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-amber-signal stroke-[1.5]" />
                  SELECT TARGET ROLE DOSSIER
                </h2>
                <span className="font-mono text-xs text-text-tertiary">
                  3 RIGOROUS BENCHMARKS
                </span>
              </div>

              {/* 3D Tilt Role Dossier Cards */}
              <div
                role="radiogroup"
                aria-label="Interview target role dossiers"
                className="space-y-4"
              >
                {ROLES.map((role) => (
                  <RoleDossierCard
                    key={role.id}
                    id={role.id}
                    title={role.title}
                    subheadline={role.subheadline}
                    description={role.description}
                    tags={role.tags}
                    benchmark={role.benchmark}
                    icon={role.icon}
                    iconColor={role.iconColor}
                    isSelected={selectedRoleId === role.id}
                    onSelect={handleSelectRole}
                  />
                ))}
              </div>
            </div>

            {/* Optional JD & Resume Intake Section */}
            <div className="p-5 rounded-2xl bg-surface-panel/90 border border-border-subtle space-y-4">
              <div className="flex items-center justify-between border-b border-border-subtle/50 pb-2.5">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-signal" />
                  <span className="font-mono text-xs uppercase tracking-wider text-text-primary font-semibold">
                    Dynamic Calibration (Optional)
                  </span>
                </div>
                <span className="font-mono text-[10px] uppercase px-2 py-0.5 rounded bg-amber-subtle text-amber-signal border border-amber-500/30 font-semibold">
                  JD + Resume Adaptive
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* JD Input + Upload */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <label htmlFor="jd-input" className="flex items-center gap-1.5 text-xs font-mono text-text-secondary">
                      <FileText className="w-3.5 h-3.5 text-amber-signal" />
                      <span>Target Job Description</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => jdFileInputRef.current?.click()}
                      disabled={jdUploading}
                      className="inline-flex items-center gap-1 text-[11px] font-mono text-amber-signal hover:text-amber-400 bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/20 px-2 py-0.5 rounded transition-colors disabled:opacity-50 cursor-pointer"
                    >
                      {jdUploading ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span>Extracting...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-3 h-3" />
                          <span>Upload PDF (optional)</span>
                        </>
                      )}
                    </button>
                    <input
                      ref={jdFileInputRef}
                      type="file"
                      accept=".pdf,application/pdf"
                      className="hidden"
                      onChange={(e) => handleFileUpload(e, 'jd')}
                    />
                  </div>

                  <textarea
                    id="jd-input"
                    rows={3}
                    value={jdText}
                    onChange={(e) => setJdText(e.target.value)}
                    placeholder="Paste job requirements or upload PDF above to generate tailored questions..."
                    className="w-full text-xs font-mono bg-surface-ground/90 border border-border-subtle focus:border-amber-signal/60 rounded-xl p-3 text-text-primary placeholder:text-text-tertiary/60 outline-none transition-colors resize-none"
                  />

                  {jdStatus && (
                    <div
                      className={`text-[11px] font-mono flex items-center gap-1.5 pt-0.5 transition-all ${
                        jdStatus.type === 'success' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {jdStatus.type === 'success' ? (
                        <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                      )}
                      <span>{jdStatus.message}</span>
                    </div>
                  )}
                </div>

                {/* Resume Input + Upload */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <label htmlFor="resume-input" className="flex items-center gap-1.5 text-xs font-mono text-text-secondary">
                      <FileText className="w-3.5 h-3.5 text-mint-eval" />
                      <span>Candidate Resume / Highlights</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => resumeFileInputRef.current?.click()}
                      disabled={resumeUploading}
                      className="inline-flex items-center gap-1 text-[11px] font-mono text-mint-eval hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 px-2 py-0.5 rounded transition-colors disabled:opacity-50 cursor-pointer"
                    >
                      {resumeUploading ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin" />
                          <span>Extracting...</span>
                        </>
                      ) : (
                        <>
                          <Upload className="w-3 h-3" />
                          <span>Upload PDF (optional)</span>
                        </>
                      )}
                    </button>
                    <input
                      ref={resumeFileInputRef}
                      type="file"
                      accept=".pdf,application/pdf"
                      className="hidden"
                      onChange={(e) => handleFileUpload(e, 'resume')}
                    />
                  </div>

                  <textarea
                    id="resume-input"
                    rows={3}
                    value={resumeText}
                    onChange={(e) => setResumeText(e.target.value)}
                    placeholder="Paste candidate background or upload PDF above for tailored probing..."
                    className="w-full text-xs font-mono bg-surface-ground/90 border border-border-subtle focus:border-mint-eval/60 rounded-xl p-3 text-text-primary placeholder:text-text-tertiary/60 outline-none transition-colors resize-none"
                  />

                  {resumeStatus && (
                    <div
                      className={`text-[11px] font-mono flex items-center gap-1.5 pt-0.5 transition-all ${
                        resumeStatus.type === 'success' ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {resumeStatus.type === 'success' ? (
                        <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                      ) : (
                        <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                      )}
                      <span>{resumeStatus.message}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Architecture Telemetry Metrics Banner */}
            <div className="p-4 rounded-xl bg-surface-panel/60 border border-border-subtle flex flex-wrap items-center justify-between gap-4 font-mono text-xs text-text-tertiary">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-mint-eval stroke-[1.5]" />
                <span>VISION LANDMARKER: <strong className="text-text-primary">15 FPS</strong></span>
              </div>
              <span className="text-border-subtle hidden sm:inline">|</span>
              <div>
                <span>SPEECH PIPELINE: <strong className="text-text-primary">WHISPER-V3</strong></span>
              </div>
              <span className="text-border-subtle hidden sm:inline">|</span>
              <div>
                <span>EVALUATION ENGINE: <strong className="text-text-primary">GROQ / QWEN 27B</strong></span>
              </div>
            </div>
          </div>

          {/* Right Column: Hardware Diagnostics Console (col-span-5) */}
          <div className="lg:col-span-5 lg:sticky lg:top-24">
            <HardwareDiagnosticsConsole
              selectedRoleTitle={selectedRole.title}
              isLoading={isLoading}
              onEnterRoom={handleEnterRoom}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
