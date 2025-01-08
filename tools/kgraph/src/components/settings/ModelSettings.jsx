import { useState, useEffect, useRef, useCallback } from 'react';
import { fetchModels } from '../../services/openRouterApi';
import { aiService } from '../../services/ai';

function ModelSettings() {
  const [model, setModel] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [temperature, setTemperature] = useState(0.7);
  const [saveStatus, setSaveStatus] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Load saved settings
    const savedSettings = localStorage.getItem('modelSettings');
    if (savedSettings) {
      const { model: savedModel, temperature: savedTemp } = JSON.parse(savedSettings);
      setModel(savedModel);
      setTemperature(savedTemp);
    }
    loadModels();
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }

    function handleEscape(event) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscape);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchModels();
      setModels(data);
      if (data.length > 0 && !model) {
        setModel(data[0].id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredModels = models.filter(m => 
    m.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleKeyDown = useCallback((e) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(i => Math.min(i + 1, filteredModels.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredModels[selectedIndex]) {
          setModel(filteredModels[selectedIndex].id);
          setIsOpen(false);
        }
        break;
    }
  }, [isOpen, filteredModels, selectedIndex]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchTerm]);

  return (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium mb-2">Model</label>
        <div className="relative" ref={dropdownRef}>
          <div
            onClick={() => setIsOpen(!isOpen)}
            className="w-full px-3 py-2 bg-[var(--node-bg)] border border-[var(--border)] rounded focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer flex justify-between items-center"
          >
            <span>{model || 'Select a model'}</span>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>

          {isOpen && (
            <div className="absolute z-10 w-full mt-1 bg-[var(--node-bg)] border border-[var(--border)] rounded shadow-lg">
              <div className="p-2">
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search models..."
                  className="w-full px-3 py-2 bg-[var(--node-bg)] border border-[var(--border)] rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onKeyDown={(e) => {
                    if (e.key === 'Escape') {
                      setIsOpen(false);
                    } else {
                      handleKeyDown(e);
                    }
                  }}
                  onClick={(e) => e.stopPropagation()}
                  autoFocus
                />
              </div>

              {loading ? (
                <div className="p-4 text-center text-gray-500">Loading models...</div>
              ) : error ? (
                <div className="p-4 text-center text-red-500">{error}</div>
              ) : (
                <div className="max-h-[50vh] overflow-auto">
                  {filteredModels.map((m) => (
                    <div
                      key={m.id}
                      onClick={() => {
                        setModel(m.id);
                        setIsOpen(false);
                      }}
                      className={`px-3 py-2 cursor-pointer hover:bg-blue-500 hover:text-white ${
                        model === m.id || filteredModels.indexOf(m) === selectedIndex ? 'bg-blue-500 text-white' : ''
                      }`}
                    >
                      {m.id}
                    </div>
                  ))}
                  {filteredModels.length === 0 && (
                    <div className="p-4 text-center text-gray-500">No models found</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-2">
          Temperature: {temperature}
        </label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={temperature}
          onChange={(e) => setTemperature(parseFloat(e.target.value))}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-500">
          <span>More Focused</span>
          <span>More Creative</span>
        </div>
      </div>

      <div className="pt-4">
        <button
          onClick={() => {
            localStorage.setItem('modelSettings', JSON.stringify({
              model,
              temperature
            }));
            aiService.updateSettings();
            setSaveStatus('saved');
            setTimeout(() => setSaveStatus(''), 2000);
          }}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors relative"
        >
          {saveStatus === 'saved' ? 'Settings Saved!' : 'Save Changes'}
        </button>
      </div>
    </div>
  );
}

export default ModelSettings;
