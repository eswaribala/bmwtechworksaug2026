import { usePipeline } from '../context/PipelineContext';

interface FileFilterProps {
  showRunSelect?: boolean;
}

export default function FileFilter({ showRunSelect = true }: FileFilterProps) {
  const {
    datasetFilter,
    setDatasetFilter,
    selectedRunId,
    setSelectedRunId,
    filteredHistory,
    historyLoading,
    refreshHistory,
  } = usePipeline();

  return (
    <div className="file-filter-bar">
      <div className="file-filter-group">
        <label className="file-filter-label">Dataset</label>
        <div className="segmented-control">
          <button
            type="button"
            className={`segmented-btn ${datasetFilter === 'telemetry' ? 'active' : ''}`}
            onClick={() => {
              setDatasetFilter('telemetry');
              setSelectedRunId(null);
            }}
          >
            Telemetry
          </button>
          <button
            type="button"
            className={`segmented-btn ${datasetFilter === 'vehicle_master' ? 'active' : ''}`}
            onClick={() => {
              setDatasetFilter('vehicle_master');
              setSelectedRunId(null);
            }}
          >
            Vehicle Master
          </button>
        </div>
      </div>

      {showRunSelect && (
        <div className="file-filter-group" style={{ flex: 1, maxWidth: 360 }}>
          <label className="file-filter-label">Processed File</label>
          <select
            className="filter-select"
            value={selectedRunId ?? (filteredHistory[0]?.run_id || '')}
            onChange={e => setSelectedRunId(e.target.value || null)}
            disabled={historyLoading || filteredHistory.length === 0}
          >
            {filteredHistory.length === 0 ? (
              <option value="">No files processed yet</option>
            ) : (
              filteredHistory.map(h => (
                <option key={h.run_id} value={h.run_id}>
                  {h.filename} · {h.timestamp.slice(0, 19).replace('T', ' ')} (Score: {h.quality_score.toFixed(1)})
                </option>
              ))
            )}
          </select>
        </div>
      )}

      <button
        type="button"
        className="btn btn-ghost"
        style={{ fontSize: 12, padding: '0.4rem 0.75rem', alignSelf: 'flex-end' }}
        onClick={() => refreshHistory()}
        title="Refresh processed files list"
      >
        Refresh
      </button>
    </div>
  );
}
