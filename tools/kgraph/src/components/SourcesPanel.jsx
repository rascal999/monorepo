import { useState, useEffect } from 'react';
import { aiService } from '../services/aiService';

function SourcesPanel({ selectedNode, nodeData, onUpdateData }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchSources = async () => {
    if (!selectedNode?.data?.label) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await aiService.searchSources(selectedNode.data.label);
      if (result.success) {
        onUpdateData(selectedNode.id, 'sources', result.sources);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Search only if no sources exist for this node
  useEffect(() => {
    if (selectedNode && !nodeData?.sources) {
      searchSources();
    }
  }, [selectedNode?.id]);

  if (!selectedNode) {
    return (
      <div className="flex-1 p-4 flex items-center justify-center text-gray-500">
        Select a node to view sources
      </div>
    );
  }

  return (
    <div className="flex-1 p-4 overflow-auto">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-2">
          Sources for: {selectedNode.data.label}
        </h3>
        {loading && <p className="text-gray-500">Searching for sources...</p>}
        {error && <p className="text-red-500">{error}</p>}
      </div>

      {nodeData?.sources?.length > 0 ? (
        <ul className="space-y-4">
          {nodeData.sources.map((source, index) => (
            <li key={index} className="border-b border-[var(--border)] pb-4">
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline block mb-1"
              >
                {source.title}
              </a>
              {source.description && (
                <p className="text-sm text-gray-500">{source.description}</p>
              )}
            </li>
          ))}
        </ul>
      ) : !loading && (
        <p className="text-gray-500">No sources found</p>
      )}

      {!loading && nodeData?.sources && (
        <button
          onClick={searchSources}
          className="mt-4 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          Refresh Sources
        </button>
      )}
    </div>
  );
}

export default SourcesPanel;
