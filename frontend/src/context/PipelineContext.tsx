import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import type { HistoryRun } from '../types';

export const API_URL = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8000';

export type DatasetFilter = 'telemetry' | 'vehicle_master';

interface PipelineContextType {
  backendOnline: boolean;
  awsConnected: boolean;
  s3Bucket: string;
  history: HistoryRun[];
  historyLoading: boolean;
  datasetFilter: DatasetFilter;
  setDatasetFilter: (d: DatasetFilter) => void;
  selectedRunId: string | null;
  setSelectedRunId: (id: string | null) => void;
  selectedRun: HistoryRun | null;
  filteredHistory: HistoryRun[];
  refreshHistory: () => Promise<void>;
  refreshHealth: () => Promise<void>;
}

const PipelineContext = createContext<PipelineContextType | undefined>(undefined);

export function PipelineProvider({ children }: { children: ReactNode }) {
  const [backendOnline, setBackendOnline] = useState(false);
  const [awsConnected, setAwsConnected] = useState(false);
  const [s3Bucket, setS3Bucket] = useState('-');
  const [history, setHistory] = useState<HistoryRun[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [datasetFilter, setDatasetFilter] = useState<DatasetFilter>('telemetry');
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);

  const refreshHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        setBackendOnline(true);
        setAwsConnected(Boolean(data.aws_connected));
        setS3Bucket(data.s3_bucket ?? '-');
        return;
      }
      setBackendOnline(false);
    } catch {
      setBackendOnline(false);
      setAwsConnected(false);
    }
  }, []);

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/history`);
      if (res.ok) {
        const data = await res.json();
        setHistory(data.runs ?? []);
        setBackendOnline(true);
      } else {
        setHistory([]);
      }
    } catch {
      setHistory([]);
      setBackendOnline(false);
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshHealth();
    refreshHistory();
  }, [refreshHealth, refreshHistory]);

  const filteredHistory = history.filter(h => h.dataset === datasetFilter);
  const selectedRun =
    (selectedRunId ? filteredHistory.find(h => h.run_id === selectedRunId) : filteredHistory[0]) ?? null;

  return (
    <PipelineContext.Provider
      value={{
        backendOnline,
        awsConnected,
        s3Bucket,
        history,
        historyLoading,
        datasetFilter,
        setDatasetFilter,
        selectedRunId,
        setSelectedRunId,
        selectedRun,
        filteredHistory,
        refreshHistory,
        refreshHealth,
      }}
    >
      {children}
    </PipelineContext.Provider>
  );
}

export function usePipeline() {
  const ctx = useContext(PipelineContext);
  if (!ctx) throw new Error('usePipeline must be used within a PipelineProvider');
  return ctx;
}
