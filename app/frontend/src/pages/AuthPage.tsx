import React, { useState } from 'react';
import { Bot, Lock, Mail, ArrowRight, ShieldCheck, AlertCircle, Loader2 } from 'lucide-react';
import { apiLogin, apiSignup } from '../api/client';

interface AuthPageProps {
  initialMode?: 'login' | 'signup';
  onAuthSuccess: (user: { id: string; email: string }, token: string) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ initialMode = 'login', onAuthSuccess }) => {
  const [mode, setMode] = useState<'login' | 'signup'>(initialMode);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    const cleanEmail = email.trim();
    if (!cleanEmail || !password) {
      setErrorMsg('Please enter both email and password.');
      return;
    }
    if (password.length < 6) {
      setErrorMsg('Password must be at least 6 characters.');
      return;
    }

    setIsSubmitting(true);
    try {
      if (mode === 'signup') {
        const res = await apiSignup(cleanEmail, password);
        onAuthSuccess(res.user, res.token);
      } else {
        const res = await apiLogin(cleanEmail, password);
        onAuthSuccess(res.user, res.token);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Authentication failed. Please verify your credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-140px)] flex flex-col justify-center items-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Anti-slop Studio Card */}
        <div className="bg-surface-panel border border-border-default rounded-xl p-8 shadow-2xl relative overflow-hidden">
          {/* Subtle top indicator bar */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-amber-signal/40" />

          {/* Header */}
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-lg bg-surface-ground border border-border-default flex items-center justify-center text-amber-signal shadow-sm">
              <Bot className="w-5 h-5 stroke-[1.5]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display font-bold text-lg text-text-primary tracking-tight">
                  {mode === 'login' ? 'Candidate Sign In' : 'Create Candidate Account'}
                </h1>
                <span className="px-1.5 py-0.5 text-[9px] font-mono font-semibold rounded bg-amber-subtle text-amber-signal border border-amber-500/30">
                  JWT HS256
                </span>
              </div>
              <p className="text-[11px] font-mono text-text-tertiary">
                AUTONOMOUS HR EVALUATOR // SESSION ISOLATION
              </p>
            </div>
          </div>

          {/* Mode Switcher Tabs */}
          <div className="flex rounded-lg bg-surface-ground p-1 mb-6 border border-border-subtle text-xs font-mono">
            <button
              type="button"
              onClick={() => {
                setMode('login');
                setErrorMsg(null);
              }}
              className={`flex-1 py-1.5 rounded-md font-medium transition-all ${
                mode === 'login'
                  ? 'bg-amber-signal/15 text-amber-signal border border-amber-500/40 shadow-sm'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              SIGN IN
            </button>
            <button
              type="button"
              onClick={() => {
                setMode('signup');
                setErrorMsg(null);
              }}
              className={`flex-1 py-1.5 rounded-md font-medium transition-all ${
                mode === 'signup'
                  ? 'bg-amber-signal/15 text-amber-signal border border-amber-500/40 shadow-sm'
                  : 'text-text-secondary hover:text-text-primary'
              }`}
            >
              SIGN UP
            </button>
          </div>

          {/* Error Banner */}
          {errorMsg && (
            <div className="mb-5 p-3 rounded-lg bg-coral-alert/10 border border-coral-alert/30 flex items-start gap-2.5 text-xs text-coral-alert font-mono">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-[11px] font-mono uppercase tracking-wider text-text-secondary mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-text-tertiary absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  autoFocus
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="candidate@example.com"
                  className="w-full pl-9 pr-3 py-2 bg-surface-ground border border-border-default rounded-lg text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-amber-signal/60 focus:ring-1 focus:ring-amber-signal/50 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-mono uppercase tracking-wider text-text-secondary mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-text-tertiary absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 bg-surface-ground border border-border-default rounded-lg text-sm text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-amber-signal/60 focus:ring-1 focus:ring-amber-signal/50 font-mono"
                />
              </div>
              {mode === 'signup' && (
                <p className="mt-1 text-[10px] font-mono text-text-tertiary">
                  Minimum 6 characters. Passwords are securely hashed with bcrypt.
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 py-2.5 px-4 rounded-lg bg-amber-signal text-surface-ground font-display font-bold text-sm tracking-wide hover:bg-amber-400 active:scale-[0.99] transition-all flex items-center justify-center gap-2 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>AUTHENTICATING...</span>
                </>
              ) : mode === 'login' ? (
                <>
                  <span>SIGN IN TO COCKPIT</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              ) : (
                <>
                  <span>CREATE ACCOUNT</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Toggle Helper Link */}
          <div className="mt-6 pt-5 border-t border-border-subtle text-center text-xs text-text-secondary font-mono">
            {mode === 'login' ? (
              <p>
                Don't have an account?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('signup');
                    setErrorMsg(null);
                  }}
                  className="text-amber-signal hover:underline font-semibold"
                >
                  Sign up now
                </button>
              </p>
            ) : (
              <p>
                Already registered?{' '}
                <button
                  type="button"
                  onClick={() => {
                    setMode('login');
                    setErrorMsg(null);
                  }}
                  className="text-amber-signal hover:underline font-semibold"
                >
                  Sign in
                </button>
              </p>
            )}
          </div>

          {/* Security Subtext */}
          <div className="mt-4 flex items-center justify-center gap-1.5 text-[10px] font-mono text-text-tertiary">
            <ShieldCheck className="w-3.5 h-3.5 text-mint-eval" />
            <span>24H SESSION ISOLATION & ENCRYPTED STORAGE</span>
          </div>
        </div>
      </div>
    </div>
  );
};
