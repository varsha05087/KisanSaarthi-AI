import React, { useState, useEffect } from 'react';
import {
  ClipboardList,
  Tractor,
  Sprout,
  ShieldCheck,
  Clock,
  ChevronRight,
  CheckCircle2,
  PlusCircle,
  User,
  Phone,
} from 'lucide-react';
import { useTranslation } from '../i18n';
import { getRequests } from '../services/api';
import { useFarmerAuth } from '../context/FarmerAuthContext';
import { formatPhoneNumber } from '../services/farmerAuth';

export default function Requests({ onBackToHome, onOpenTractorBooking, onOpenInsuranceAssistance }) {
  const { t, lang } = useTranslation();
  const { currentFarmer } = useFarmerAuth();
  const [activeFilter, setActiveFilter] = useState('all');
  const [requestsList, setRequestsList] = useState([]);

  useEffect(() => {
    async function fetchReqs() {
      if (currentFarmer?.id) {
        const data = await getRequests(currentFarmer.id);
        setRequestsList(data);
      }
    }
    fetchReqs();
  }, [currentFarmer]);

  // Navigate to conversational Assistant to book a tractor
  const handleBookTractorClick = () => {
    if (onOpenTractorBooking) {
      onOpenTractorBooking();
    }
  };

  // Navigate to conversational Assistant for insurance assistance
  const handleInsuranceClick = () => {
    if (onOpenInsuranceAssistance) {
      onOpenInsuranceAssistance();
    }
  };

  const filters = [
    { id: 'all', label: t('requests.all') },
    { id: 'tractor', label: t('requests.tractor') },
    { id: 'crop', label: t('requests.crop') },
    { id: 'insurance', label: t('requests.insurance') },
  ];

  const filtered = requestsList.filter((r) => activeFilter === 'all' || r.type === activeFilter);

  const getIcon = (type) => {
    switch (type) {
      case 'tractor':
        return Tractor;
      case 'insurance':
        return ShieldCheck;
      default:
        return Sprout;
    }
  };

  const defaultFarmerName = lang === 'hi' ? 'किसान भाई' : lang === 'te' ? 'రైతు' : 'Farmer';

  return (
    <div className="pb-28 pt-4 px-4 sm:px-6 space-y-5 max-w-2xl mx-auto animate-fadeIn select-none">
      {/* Page Title & Farmer Identity Badge */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-earth-text tracking-tight">
            {t('nav.requests')}
          </h2>
          <div className="flex items-center gap-2 text-xs text-earth-muted mt-0.5">
            <span className="font-bold text-forest flex items-center gap-1">
              <User className="w-3.5 h-3.5" /> {currentFarmer?.name || defaultFarmerName}
            </span>
            <span>•</span>
            <span className="font-mono">
              {formatPhoneNumber(currentFarmer?.phone) || '98765 43210'}
            </span>
          </div>
        </div>
        <div className="w-10 h-10 rounded-2xl bg-forest-50 text-forest flex items-center justify-center">
          <ClipboardList className="w-5 h-5" />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
        {filters.map((f) => (
          <button
            key={f.id}
            type="button"
            onClick={() => setActiveFilter(f.id)}
            className={`
              px-4 py-2 rounded-full text-xs font-bold transition-all flex-shrink-0
              ${
                activeFilter === f.id
                  ? 'bg-forest text-white shadow-sm'
                  : 'bg-white text-earth-muted border border-earth-border hover:bg-earth-subtle'
              }
            `}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Tractor Filter Active: Action to book a tractor */}
      {activeFilter === 'tractor' && filtered.length > 0 && (
        <div className="flex justify-end">
          <button
            type="button"
            data-testid="requests-book-tractor-btn"
            onClick={handleBookTractorClick}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-xs shadow-sm transition-all active:scale-95"
          >
            <Tractor className="w-4 h-4" />
            <span>{t('requests.bookTractorBtn')}</span>
          </button>
        </div>
      )}

      {/* Insurance Filter Active: Action to get insurance assistance */}
      {activeFilter === 'insurance' && filtered.length > 0 && (
        <div className="flex justify-end">
          <button
            type="button"
            data-testid="requests-insurance-btn"
            onClick={handleInsuranceClick}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-xs shadow-sm transition-all active:scale-95"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{t('requests.getInsuranceBtn')}</span>
          </button>
        </div>
      )}

      {/* Requests List or Empty State */}
      {filtered.length === 0 ? (
        <div className="p-8 rounded-3xl bg-white border border-dashed border-earth-border text-center space-y-3">
          <div className="w-14 h-14 rounded-2xl bg-forest-50 text-forest mx-auto flex items-center justify-center text-2xl">
            📋
          </div>
          <h3 className="font-bold text-base text-earth-text">
            {currentFarmer?.name
              ? lang === 'hi'
                ? `${currentFarmer.name} के लिए अभी कोई अनुरोध नहीं है`
                : lang === 'te'
                ? `${currentFarmer.name} గారికి ఇంకా అభ్యర్థనలు లేవు`
                : `No requests yet for ${currentFarmer.name}`
              : t('requests.emptyTitle')}
          </h3>
          <p className="text-xs text-earth-muted max-w-xs mx-auto">
            {t('requests.emptySubtitle')}
          </p>
          {activeFilter === 'insurance' ? (
            <button
              type="button"
              data-testid="requests-insurance-btn"
              onClick={handleInsuranceClick}
              className="mt-2 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-xs shadow-md transition-all active:scale-95"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>{t('requests.getInsuranceBtn')}</span>
            </button>
          ) : (
            <button
              type="button"
              data-testid="requests-book-tractor-btn"
              onClick={handleBookTractorClick}
              className="mt-2 inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-forest hover:bg-forest-600 text-white font-bold text-xs shadow-md transition-all active:scale-95"
            >
              <Tractor className="w-4 h-4" />
              <span>
                {`${t('requests.bookTractorBtn')}${currentFarmer?.name ? ` (${currentFarmer.name})` : ''}`}
              </span>
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((req) => {
            const Icon = getIcon(req.type);
            return (
              <div
                key={req.id}
                className="p-4 rounded-2xl bg-white border border-earth-border/80 shadow-farmer hover:shadow-farmer-lg transition-all"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-xl bg-forest-50 text-forest flex items-center justify-center flex-shrink-0 mt-0.5">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-earth-text text-sm sm:text-base leading-snug">
                        {req.title}
                      </h3>
                      <div className="flex items-center gap-2 text-xs text-earth-muted mt-1">
                        <Clock className="w-3.5 h-3.5" />
                        <span>{req.date}</span>
                        <span>•</span>
                        <span>ID: {req.id}</span>
                      </div>
                      <div className="mt-1 text-[11px] font-semibold text-forest flex items-center gap-1">
                        <span>{t('requests.farmerPrefix')} {req.farmerName || currentFarmer?.name}</span>
                      </div>
                    </div>
                  </div>

                  <span className={`text-xs font-bold px-2.5 py-1 rounded-full border flex-shrink-0 ${req.statusColor}`}>
                    {req.status}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
