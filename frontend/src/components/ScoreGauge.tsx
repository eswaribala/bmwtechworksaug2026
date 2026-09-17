import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { getScoreColor } from '../utils/constants';

interface ScoreGaugeProps {
  score: number | null | undefined;
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
  const isAvailable = score !== null && score !== undefined && !Number.isNaN(score);
  const numericScore = isAvailable ? score : 0;
  const color = isAvailable ? getScoreColor(numericScore) : 'var(--text-muted)';

  const segments = [
    { name: 'Critical',   value: 50,  color: '#FF4757' },
    { name: 'Poor',       value: 20,  color: '#FF6B35' },
    { name: 'Acceptable', value: 10,  color: '#FFA500' },
    { name: 'Good',       value: 10,  color: '#0066CC' },
    { name: 'Excellent',  value: 10,  color: '#00C48C' },
  ];

  // Map score 0–100 to angle 180–0 (half circle)
  const needleAngle = isAvailable ? 180 - (numericScore / 100) * 180 : 90;

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
            {segments.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} opacity={isAvailable ? 0.9 : 0.25} />
            ))}
          </Pie>
          {isAvailable && (
            <Pie
              dataKey="value"
              data={[{ value: 1 }]}
              cx="50%"
              cy="90%"
              startAngle={180}
              endAngle={0}
              innerRadius={0}
              outerRadius={0}
              stroke="none"
              isAnimationActive={false}
              label={({ cx, cy }) => renderNeedle(cx, cy, needleAngle, 85, color)}
            />
          )}
        </PieChart>
      </ResponsiveContainer>

      <div className="score-gauge-value" style={{ marginTop: '-20px' }}>
        <div style={{ fontSize: 36, fontWeight: 900, color, lineHeight: 1 }}>
          {isAvailable ? numericScore.toFixed(1) : '-'}
        </div>
        <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginTop: 4, fontWeight: 600 }}>
          {label}
        </div>
      </div>
    </div>
  );
}
