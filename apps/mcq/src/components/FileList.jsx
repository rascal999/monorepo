import { useState, useEffect } from 'react';
import { QuestionHandler } from '../utils/QuestionHandler';
import { LocalStorageManager } from '../utils/LocalStorageManager';
import { UploadSection } from './UploadSection';

export function FileList({ files, onFilesUpdate, onQuestionsLoaded, uploadedFiles, section }) {
  const [preferences, setPreferences] = useState(LocalStorageManager.getQuizPreferences());
  const [allFiles, setAllFiles] = useState([]);
  const [directoryFiles, setDirectoryFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadAllFiles = async () => {
      try {
        setIsLoading(true);
        // Load questions from directory
        const directoryFilesPromises = await LocalStorageManager.loadQuestionsFromDirectory();
        const resolvedFiles = await Promise.all(directoryFilesPromises);
        
        if (!isMounted) return;
        
        setDirectoryFiles(resolvedFiles);
        
        // Get uploaded files
        const uploadedFiles = LocalStorageManager.getUploadedFiles();
        
        // Merge with uploaded files, preferring uploaded versions if they exist
        const uploadedFilesMap = new Map(uploadedFiles.map(f => [f.id, f]));
        const mergedFiles = resolvedFiles.map(f => uploadedFilesMap.get(f.id) || f);
        
        // Add any uploaded files that don't correspond to directory files
        uploadedFiles.forEach(f => {
          if (!mergedFiles.find(mf => mf.id === f.id)) {
            mergedFiles.push(f);
          }
        });

        if (!isMounted) return;

        setAllFiles(mergedFiles);
        onFilesUpdate(mergedFiles);
      } catch (error) {
        console.error('Error loading files:', error);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadAllFiles();

    return () => {
      isMounted = false;
    };
  }, []); // Remove files and onFilesUpdate from dependencies

  const handleDelete = (id) => {
    const updatedFiles = files.filter(file => file.id !== id);
    if (LocalStorageManager.saveUploadedFiles(updatedFiles)) {
      onFilesUpdate(updatedFiles);
    }
  };

  const handleLoad = (file) => {
    try {
      const loadedData = JSON.parse(file.content);
      const preparedQuestions = QuestionHandler.prepareQuestions(loadedData.questions, preferences.randomizeQuestions);
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

  const renderQuizItem = (file, isDirectoryFile) => {
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
          {!isDirectoryFile && (
            <button 
              onClick={() => handleDelete(file.id)}
              className="delete-btn"
              title="Delete Quiz"
            >
              ×
            </button>
          )}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return <div className="loading">Loading quizzes...</div>;
  }

  if (allFiles.length === 0) {
    return null;
  }

  const uploadedQuizzes = allFiles.filter(file => !directoryFiles.some(df => df.id === file.id));
  const availableQuizzes = allFiles.filter(file => directoryFiles.some(df => df.id === file.id));

  // Only render quiz sections if we're in the upload section
  if (section !== 'upload') {
    return null;
  }

  return (
    <div className="quiz-sections">
      {uploadedQuizzes.length > 0 && (
        <div className="quiz-section">
          <h2 className="section-title">My Uploaded Quizzes</h2>
          <div className="files-list">
            {uploadedQuizzes.map(file => renderQuizItem(file, false))}
          </div>
        </div>
      )}

      {availableQuizzes.length > 0 && (
        <div className="quiz-section">
          <h2 className="section-title">Available Quizzes</h2>
          <div className="files-list">
            {availableQuizzes.map(file => renderQuizItem(file, true))}
          </div>
        </div>
      )}

      <div className="quiz-section">
        <h2 className="section-title">Upload Your Quiz</h2>
        <UploadSection 
          uploadedFiles={uploadedFiles || files}
          onFilesUpdate={onFilesUpdate}
          onQuestionsLoaded={onQuestionsLoaded}
        />
      </div>

      <div className="quiz-section">
        <h2 className="section-title">Options</h2>
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
            <label className="option-label">
              <input
                type="checkbox"
                checked={preferences.randomizeQuestions}
                onChange={(e) => handlePreferencesChange({ randomizeQuestions: e.target.checked })}
              />
              Randomize question order
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}
