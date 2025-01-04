export function QuizItem({ file, isDirectoryFile, onLoad, onDelete }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${month}-${day} ${hours}:${minutes}`;
  };

  const getQuizStats = (file) => {
    if (!file.stats) return null;
    const { bestScore, attempts } = file.stats;
    if (!attempts || attempts === 0) return null;
    return {
      bestScore: bestScore !== undefined ? `${Math.round(bestScore * 100)}%` : '-',
      attempts
    };
  };

  const stats = getQuizStats(file);
  const questions = JSON.parse(file.content).questions;
  
  return (
    <div className="file-item">
      <div className="file-info">
        <div className="file-main">
          <span className="file-title">{file.title}</span>
          <span className="file-meta">
            {questions.length}q • {formatTimestamp(file.timestamp)}
          </span>
        </div>
        {stats && (
          <div className="file-stats">
            <span title="Best Score">🎯 {stats.bestScore}</span>
            <span title="Attempts">🔄 {stats.attempts}</span>
          </div>
        )}
      </div>
      <div className="file-actions">
        <button 
          onClick={() => onLoad(file)}
          className="load-btn"
          title="Start Quiz"
        >
          Start
        </button>
        {!isDirectoryFile && (
          <button 
            onClick={() => onDelete(file.id)}
            className="delete-btn"
            title="Delete Quiz"
          >
            ×
          </button>
        )}
      </div>
    </div>
  );
}
