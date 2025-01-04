import { useState } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, PlusIcon } from '@heroicons/react/24/outline';

function SidebarPanel({ graphs, activeGraph, onCreateGraph, onSelectGraph, onClearData }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [newGraphTitle, setNewGraphTitle] = useState('');

  const handleCreateClick = () => {
    setIsCreating(true);
    setIsExpanded(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (newGraphTitle.trim()) {
      onCreateGraph(newGraphTitle.trim());
      setNewGraphTitle('');
      setIsCreating(false);
    }
  };

  return (
    <div className={`panel h-full border-r flex flex-col ${isExpanded ? 'p-4' : 'p-2'}`}>
      <div className="flex items-center justify-between mb-4">
        {isExpanded && <h2 className="text-lg font-semibold">Knowledge Graphs</h2>}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-1 hover:bg-[var(--node-bg)] rounded"
        >
          {isExpanded ? (
            <ChevronLeftIcon className="w-5 h-5" />
          ) : (
            <ChevronRightIcon className="w-5 h-5" />
          )}
        </button>
      </div>

      {isExpanded && (
        <>
          <button
            onClick={handleCreateClick}
            className="flex items-center gap-2 mb-4 px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            <PlusIcon className="w-5 h-5" />
            New Graph
          </button>

          {isCreating && (
            <form onSubmit={handleSubmit} className="mb-4">
              <input
                type="text"
                value={newGraphTitle}
                onChange={(e) => setNewGraphTitle(e.target.value)}
                placeholder="Enter graph title..."
                className="w-full px-3 py-2 bg-[var(--node-bg)] border border-[var(--border)] rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                autoFocus
              />
            </form>
          )}

          <div className="flex-1 overflow-auto">
            {graphs.map(graph => (
              <button
                key={graph.id}
                onClick={() => onSelectGraph(graph)}
                className={`w-full px-3 py-2 text-left rounded mb-2 hover:bg-[var(--node-bg)] transition-colors ${
                  activeGraph?.id === graph.id ? 'bg-[var(--node-bg)]' : ''
                }`}
              >
                <div>{graph.title}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(parseInt(graph.id)).toLocaleDateString()} • {Array.isArray(graph.nodes) ? graph.nodes.length : 0} node{(!graph.nodes || graph.nodes.length !== 1) ? 's' : ''}
                </div>
              </button>
            ))}
          </div>

          <div className="mt-auto pt-4 border-t border-[var(--border)]">
            <button
              onClick={() => {
                if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
                  onClearData();
                }
              }}
              className="w-full px-3 py-2 text-red-500 hover:bg-red-500 hover:text-white rounded transition-colors"
            >
              Clear All Data
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default SidebarPanel;
