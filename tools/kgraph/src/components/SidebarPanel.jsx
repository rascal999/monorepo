import { useState, useMemo } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, PlusIcon, TrashIcon, EllipsisVerticalIcon } from '@heroicons/react/24/outline';
import SettingsPanel from './settings/SettingsPanel';

function SidebarPanel({ graphs, activeGraph, onCreateGraph, onSelectGraph, onDeleteGraph, onClearData }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [newGraphTitle, setNewGraphTitle] = useState('');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredGraphs = useMemo(() => {
    if (!searchTerm.trim()) return graphs;
    return graphs.filter(graph => 
      graph.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [graphs, searchTerm]);

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
    <>
    <div className={`panel h-full border-r flex flex-col ${isExpanded ? 'p-4' : 'p-2'}`}>
      <div className="flex items-center justify-between mb-4">
        {isExpanded && <h2 className="text-lg font-semibold">Knowledge Graphs</h2>}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(true)}
            className="p-1 hover:bg-[var(--node-bg)] rounded"
          >
            <EllipsisVerticalIcon className="w-5 h-5" />
          </button>
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

          <div className="mb-4">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search graphs..."
              className="w-full px-3 py-2 bg-[var(--node-bg)] border border-[var(--border)] rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

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
            {filteredGraphs.map(graph => (
              <div
                key={graph.id}
                onClick={() => onSelectGraph(graph)}
                className={`w-full px-3 py-2 text-left rounded mb-2 hover:bg-[var(--node-bg)] transition-colors cursor-pointer ${
                  activeGraph?.id === graph.id ? 'bg-[var(--node-bg)]' : ''
                }`}
              >
                <div className="flex justify-between items-center">
                  <span>{graph.title}</span>
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Are you sure you want to delete this graph?')) {
                        onDeleteGraph(graph.id);
                      }
                    }}
                    className="p-1 hover:bg-[var(--node-bg)] rounded opacity-50 hover:opacity-100 cursor-pointer"
                  >
                    <TrashIcon className="w-4 h-4 text-red-500" />
                  </div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(parseInt(graph.id)).toLocaleDateString()} • {Array.isArray(graph.nodes) ? graph.nodes.length : 0} node{(!graph.nodes || graph.nodes.length !== 1) ? 's' : ''}
                </div>
              </div>
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
    {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}
    </>
  );
}

export default SidebarPanel;
