import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { getScoreColor } from '../data/mockData';

interface ScoreGaugeProps {
  score: number;
  label: string;
}

const RADIAN = Math.PI / 180;

function renderNeedle(cx: number, cy: number, angle: number, r: number, color: string) {
  const x = cx + r * Math.cos(-angle * RADIAN);
  const y = cy + r * Math.sin(-angle * RADIAN);
  return (
    <g>
      <circle cx={cx} cy={cy} r={6} fill={color} />
      <line x1={cx} y1={cy} x2={x} y2={y} stroke={color} strokeWidth={3} strokeLinecap="round" />
    </g>
  );
}

export default function ScoreGauge({ score, label }: ScoreGaugeProps) {
  const color = getScoreColor(score);

  const segments = [
    { name: 'Critical',   value: 50,  color: '#FF4757' },
    { name: 'Poor',       value: 20,  color: '#FF6B35' },
    { name: 'Acceptable', value: 10,  color: '#FFA500' },
    { name: 'Good',       value: 10,  color: '#0066CC' },
    { name: 'Excellent',  value: 10,  color: '#00C48C' },
  ];

  // Map score 0–100 to angle 180–0 (half circle)
  const needleAngle = 180 - (score / 100) * 180;

  return (
    <div className="score-gauge-wrap">
      <ResponsiveContainer width="100%" height={180}>
        <PieChart>
          <Pie
            dataKey="value"
            data={segments}
            cx="50%"
            cy="90%"
            startAngle={180}
            endAngle={0}
            innerRadius={70}
            outerRadius={100}
            stroke="none"
          >
            {segments.map((seg, i) => (
              <Cell key={i} fill={seg.color} opacity={0.85} />
            ))}
          </Pie>
          {/* Needle rendered as custom active shape hack via label */}
          <Pie
            dataKey="value"
            data={[{ value: 1 }]}
            cx="50%"
            cy="90%"
            innerRadius={0}
            outerRadius={0}
            startAngle={180}
            endAngle={0}
            label={({ cx, cy }: { cx: number; cy: number }) =>
              renderNeedle(cx, cy, needleAngle, 85, color)
            }
            labelLine={false}
            stroke="none"
          />
        </PieChart>
      </ResponsiveContainer>

      <div className="score-gauge-number" style={{ color }}>
        {score.toFixed(1)}
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>/ 100</div>
      <div className={`badge badge-${label.toLowerCase()}`}>
        {label}
      </div>
    </div>
  );
}
