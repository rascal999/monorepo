import { useState } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import TabBar from '../TabBar';
import ModelSettings from './ModelSettings';

function SettingsPanel({ onClose }) {
  const [activeTab, setActiveTab] = useState('model');

  const tabs = [
    { id: 'model', icon: null, label: 'Model' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'model':
        return <ModelSettings />;
      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center z-50">
      <div className="bg-[#1e1e1e] rounded-lg shadow-xl w-[800px] h-[90vh] flex flex-col border border-[var(--border)]">
        <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
          <h2 className="text-lg font-semibold">Settings</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-[var(--node-bg)] rounded"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        <div className="flex border-b border-[var(--border)]">
          {tabs.map(({ id, icon: Icon, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
                activeTab === id ? 'border-blue-500' : 'border-transparent'
              }`}
            >
              {Icon && <Icon className="w-5 h-5" />}
              {label}
            </button>
          ))}
        </div>

        <div className="p-4 overflow-y-auto flex-1">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
