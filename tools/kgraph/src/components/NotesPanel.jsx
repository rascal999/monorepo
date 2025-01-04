function NotesPanel({ value, onChange }) {
  return (
    <textarea
      value={value || ''}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Add your notes here..."
      className="w-full h-full min-h-[200px] p-3 bg-[var(--node-bg)] rounded-lg border border-[var(--border)] focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
}

export default NotesPanel;
