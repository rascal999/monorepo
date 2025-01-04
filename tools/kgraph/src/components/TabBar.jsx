import { ChatBubbleLeftIcon, DocumentTextIcon, AcademicCapIcon } from '@heroicons/react/24/outline';

function TabBar({ activeTab, onTabChange, onNodeSelect }) {
  const tabs = [
    { id: 'chat', icon: ChatBubbleLeftIcon, label: 'Chat' },
    { id: 'notes', icon: DocumentTextIcon, label: 'Notes' },
    { id: 'quiz', icon: AcademicCapIcon, label: 'Quiz' }
  ];

  return (
    <div className="flex border-b border-[var(--border)]">
      {tabs.map(({ id, icon: Icon, label }) => (
        <button
          key={id}
          onClick={() => {
            onTabChange(id);
            if (id === 'chat') {
              onNodeSelect?.();
            }
          }}
          className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
            activeTab === id ? 'border-blue-500' : 'border-transparent'
          }`}
        >
          <Icon className="w-5 h-5" />
          {label}
        </button>
      ))}
    </div>
  );
}

export default TabBar;
