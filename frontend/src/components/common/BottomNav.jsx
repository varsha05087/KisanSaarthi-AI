import React from 'react';
import { Home, ClipboardList, User, Sparkles } from 'lucide-react';
import { useTranslation } from '../../i18n';

export default function BottomNav({ activeTab = 'home', onTabChange, onOpenAssistant }) {
  const { t } = useTranslation();

  const tabs = [
    {
      id: 'home',
      label: t('nav.home'),
      icon: Home,
    },
    {
      id: 'requests',
      label: t('nav.requests'),
      icon: ClipboardList,
    },
    {
      id: 'profile',
      label: t('nav.profile'),
      icon: User,
    },
  ];

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-40 bg-white border-t border-earth-border shadow-lg safe-bottom"
      role="navigation"
      aria-label="Main Navigation"
    >
      <div className="max-w-2xl mx-auto flex items-center justify-around px-2 py-1.5 sm:py-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => onTabChange(tab.id)}
              className={`
                flex flex-col items-center justify-center flex-1 py-1.5 px-2 rounded-xl transition-all duration-200
                ${isActive ? 'text-forest font-bold scale-105' : 'text-earth-muted hover:text-earth-text font-medium'}
              `}
              aria-current={isActive ? 'page' : undefined}
            >
              <div className={`relative p-1 rounded-lg ${isActive ? 'bg-forest-50' : ''}`}>
                <Icon className={`w-5 h-5 sm:w-6 sm:h-6 ${isActive ? 'stroke-[2.5px]' : 'stroke-2'}`} />
                {isActive && (
                  <span className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-forest" />
                )}
              </div>
              <span className="text-xs sm:text-sm mt-0.5 tracking-tight truncate max-w-[90px]">
                {tab.label}
              </span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
