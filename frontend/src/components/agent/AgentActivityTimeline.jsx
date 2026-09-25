import React from 'react';
import { CheckCircle2, Clock, Loader2, Sparkles, AlertCircle } from 'lucide-react';
import { useTranslation } from '../../i18n';

/**
 * Reusable Agent Activity Timeline
 * Visualizes agentic multi-step planning and orchestration
 * in farmer-friendly language without exposing technical logs.
 */
export default function AgentActivityTimeline({
  steps = [],
  title,
  className = "",
}) {
  const { t } = useTranslation();
  if (!steps || steps.length === 0) return null;

  const displayTitle = title || t('timeline.defaultTitle');

  return (
    <div className={`p-4 sm:p-5 rounded-2xl bg-white border border-earth-border shadow-farmer ${className}`}>
      <div className="flex items-center gap-2 pb-3 mb-3 border-b border-earth-border/60">
        <div className="w-7 h-7 rounded-lg bg-forest-50 text-forest flex items-center justify-center">
          <Sparkles className="w-4 h-4" />
        </div>
        <div>
          <h4 className="font-bold text-earth-text text-sm sm:text-base leading-none">
            {displayTitle}
          </h4>
          <p className="text-[11px] text-earth-muted mt-0.5">
            {t('timeline.subtitle')}
          </p>
        </div>
      </div>

      <div className="space-y-3 relative pl-2">
        {/* Vertical connector line */}
        <div className="absolute left-[17px] top-3 bottom-3 w-0.5 bg-earth-border/80" />

        {steps.map((step, idx) => {
          const isDone = step.status === 'done';
          const isInProgress = step.status === 'in_progress' || step.status === 'active';
          const isPending = step.status === 'pending';
          const isWarning = step.status === 'warning';

          return (
            <div key={step.id || idx} className="relative flex items-start gap-3 z-10">
              {/* Step indicator node */}
              <div
                className={`
                  w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 transition-all
                  ${
                    isDone
                      ? 'bg-forest text-white shadow-sm'
                      : isInProgress
                      ? 'bg-amber-500 text-white ring-4 ring-amber-100 animate-pulse'
                      : isWarning
                      ? 'bg-danger text-white'
                      : 'bg-white border-2 border-earth-border text-earth-muted'
                  }
                `}
              >
                {isDone ? (
                  <CheckCircle2 className="w-3.5 h-3.5" />
                ) : isInProgress ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : isWarning ? (
                  <AlertCircle className="w-3.5 h-3.5" />
                ) : (
                  <span className="w-1.5 h-1.5 rounded-full bg-earth-border" />
                )}
              </div>

              {/* Step content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p
                    className={`text-xs sm:text-sm font-semibold truncate ${
                      isDone
                        ? 'text-earth-text'
                        : isInProgress
                        ? 'text-amber-900 font-bold'
                        : isWarning
                        ? 'text-danger font-bold'
                        : 'text-earth-muted'
                    }`}
                  >
                    {step.title}
                  </p>
                  {step.time && (
                    <span className="text-[10px] text-earth-muted flex-shrink-0 font-medium">
                      {step.time}
                    </span>
                  )}
                </div>

                {step.detail && (
                  <p className="text-[11px] text-earth-muted mt-0.5 leading-snug">
                    {step.detail}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
