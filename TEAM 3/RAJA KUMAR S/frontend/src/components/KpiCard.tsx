import { useEffect, useRef, useState } from 'react';

interface KpiCardProps {
  label: string;
  value: number | null | undefined;
  unit?: string;
  sub?: string;
  color?: string;
  format?: 'number' | 'score' | 'percent';
}

export default function KpiCard({ label, value, unit = '', sub, color = 'var(--bmw-blue)', format = 'number' }: KpiCardProps) {
  const isAvailable = value !== null && value !== undefined && !Number.isNaN(value);
  const [display, setDisplay] = useState(0);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isAvailable) {
      setDisplay(0);
      return;
    }
    const start = 0;
    const end = value as number;
    const duration = 1200;
    const startTime = performance.now();

    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(start + (end - start) * eased);
      if (progress < 1) rafRef.current = requestAnimationFrame(animate);
    };

    rafRef.current = requestAnimationFrame(animate);
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
  }, [value, isAvailable]);

  const formatted = (() => {
    if (!isAvailable) return '-';
    if (format === 'score') return display.toFixed(1);
    if (format === 'percent') return `${display.toFixed(1)}%`;
    return Math.round(display).toLocaleString();
  })();

  return (
    <div className="kpi-card animate-in" style={{ '--accent-color': color } as React.CSSProperties}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={{ color }}>
        {formatted}
        {isAvailable && unit && <span style={{ fontSize: 16, fontWeight: 600, color: 'var(--text-secondary)', marginLeft: 4 }}>{unit}</span>}
      </div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}
