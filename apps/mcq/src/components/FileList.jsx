import { useState } from 'react';
import { QuestionHandler } from '../utils/QuestionHandler';
import { LocalStorageManager } from '../utils/LocalStorageManager';

export function FileList({ files, onFilesUpdate, onQuestionsLoaded }) {
  const [preferences, setPreferences] = useState(LocalStorageManager.getQuizPreferences());

  const handleDelete = (id) => {
    const updatedFiles = files.filter(file => file.id !== id);
    if (LocalStorageManager.saveUploadedFiles(updatedFiles)) {
      onFilesUpdate(updatedFiles);
    }
  };

  const handleLoad = (file) => {
    try {
      const loadedData = JSON.parse(file.content);
      const preparedQuestions = QuestionHandler.prepareQuestions(loadedData.questions);
      onQuestionsLoaded({
        title: loadedData.title,
        questions: preparedQuestions,
        fileId: file.id,
        preferences
      });
    } catch (error) {
      console.error('Error loading saved questions:', error);
      alert('Error loading questions from saved file.');
    }
  };

  const handlePreferencesChange = (changes) => {
    const newPrefs = { ...preferences, ...changes };
    if (LocalStorageManager.saveQuizPreferences(newPrefs)) {
      setPreferences(newPrefs);
    }
  };

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

  if (files.length === 0) {
    return null;
  }

  return (
    <div className="uploaded-section">
      <div className="files-list">
        {files.map(file => {
          const stats = getQuizStats(file);
          const questions = JSON.parse(file.content).questions;
          return (
            <div key={file.id} className="file-item">
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
                  onClick={() => handleLoad(file)}
                  className="load-btn"
                  title="Start Quiz"
                >
                  Start
                </button>
                <button 
                  onClick={() => handleDelete(file.id)}
                  className="delete-btn"
                  title="Delete Quiz"
                >
                  ×
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="quiz-options">
        <div className="option-controls">
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.showTimer}
              onChange={(e) => handlePreferencesChange({ showTimer: e.target.checked })}
            />
            Show Timer
          </label>
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.showAnswersStraightaway}
              onChange={(e) => handlePreferencesChange({ showAnswersStraightaway: e.target.checked })}
            />
            Show choices straightaway
          </label>
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.hideAnswerFeedback}
              onChange={(e) => handlePreferencesChange({ hideAnswerFeedback: e.target.checked })}
            />
            Hide answer feedback until quiz finished
          </label>
        </div>
      </div>
    </div>
  );
}
