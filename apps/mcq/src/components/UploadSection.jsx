import { useState, useEffect } from 'react';
import { QuestionHandler } from '../utils/QuestionHandler';

export function UploadSection({ onQuestionsLoaded }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const initializeStats = (questions) => ({
    totalQuestions: questions.length,
    bestScore: null,
    bestTime: null,
    timesPlayed: 0,
    averageScore: 0,
    totalCorrect: 0
  });

  useEffect(() => {
    try {
      const savedFiles = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
      const migratedFiles = savedFiles.map(file => ({
        ...file,
        stats: file.stats || initializeStats(JSON.parse(file.content).questions)
      }));
      setUploadedFiles(migratedFiles);
      localStorage.setItem('uploadedFiles', JSON.stringify(migratedFiles));
    } catch (error) {
      console.error('Error loading saved files:', error);
      setUploadedFiles([]);
    }
  }, []);

  const saveToLocalStorage = (files) => {
    try {
      localStorage.setItem('uploadedFiles', JSON.stringify(files));
      setUploadedFiles(files);
    } catch (error) {
      console.error('Error saving files:', error);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      const text = await file.text();
      const loadedData = JSON.parse(text);
      
      if (!loadedData.title || !loadedData.questions) {
        throw new Error('Missing title or questions');
      }

      if (!QuestionHandler.validateQuestions(loadedData.questions)) {
        throw new Error('Invalid question format');
      }

      const newFile = {
        id: Date.now(),
        title: loadedData.title,
        content: text,
        timestamp: new Date().toLocaleString(),
        stats: initializeStats(loadedData.questions)
      };

      const updatedFiles = [...uploadedFiles, newFile];
      saveToLocalStorage(updatedFiles);

      const preparedQuestions = QuestionHandler.prepareQuestions(loadedData.questions);
      onQuestionsLoaded({
        title: loadedData.title,
        questions: preparedQuestions,
        fileId: newFile.id
      });
    } catch (error) {
      console.error('Error loading questions:', error);
      alert('Error loading questions. Please ensure your JSON file is properly formatted.');
    } finally {
      event.target.value = '';
    }
  };

  const handleDelete = (id) => {
    const updatedFiles = uploadedFiles.filter(file => file.id !== id);
    saveToLocalStorage(updatedFiles);
  };

  const handleLoad = (file) => {
    try {
      const loadedData = JSON.parse(file.content);
      const preparedQuestions = QuestionHandler.prepareQuestions(loadedData.questions);
      onQuestionsLoaded({
        title: loadedData.title,
        questions: preparedQuestions,
        fileId: file.id
      });
    } catch (error) {
      console.error('Error loading saved questions:', error);
      alert('Error loading questions from saved file.');
    }
  };

  const updateStats = (fileId, score, timeMs) => {
    const updatedFiles = uploadedFiles.map(file => {
      if (file.id === fileId) {
        const stats = file.stats;
        const newTotalCorrect = stats.totalCorrect + score;
        const newTimesPlayed = stats.timesPlayed + 1;
        
        return {
          ...file,
          stats: {
            ...stats,
            bestScore: stats.bestScore === null ? score : Math.max(stats.bestScore, score),
            bestTime: stats.bestTime === null ? timeMs : Math.min(stats.bestTime, timeMs),
            timesPlayed: newTimesPlayed,
            averageScore: newTotalCorrect / newTimesPlayed,
            totalCorrect: newTotalCorrect
          }
        };
      }
      return file;
    });
    
    saveToLocalStorage(updatedFiles);
  };

  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.updateQuizStats = updateStats;
    }
    return () => {
      if (typeof window !== 'undefined') {
        delete window.updateQuizStats;
      }
    };
  }, [uploadedFiles]);

  return (
    <div className="section">
      <h1>MCQ Quiz App</h1>
      <p>Upload your JSON question file to begin</p>
      <input
        type="file"
        accept=".json"
        onChange={handleFileUpload}
        className="file-input"
      />

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h2>Previously Uploaded Files</h2>
          <div className="files-list">
            {uploadedFiles.map(file => (
              <div key={file.id} className="file-item">
                <div className="file-info">
                  <span className="file-title">{file.title}</span>
                  <span className="file-timestamp">{file.timestamp}</span>
                </div>
                <div className="file-actions">
                  <button 
                    onClick={() => handleLoad(file)}
                    className="load-btn"
                  >
                    Load
                  </button>
                  <button 
                    onClick={() => handleDelete(file.id)}
                    className="delete-btn"
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
