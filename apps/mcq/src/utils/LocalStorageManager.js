export class LocalStorageManager {
  static getUploadedFiles() {
    try {
      return JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
    } catch (error) {
      console.error('Error loading saved files:', error);
      return [];
    }
  }

  static saveUploadedFiles(files) {
    try {
      localStorage.setItem('uploadedFiles', JSON.stringify(files));
      return true;
    } catch (error) {
      console.error('Error saving files:', error);
      return false;
    }
  }

  static initializeStats(questions) {
    return {
      totalQuestions: questions.length,
      bestScore: null,
      bestTime: null,
      timesPlayed: 0,
      averageScore: 0,
      totalCorrect: 0
    };
  }

  static updateFileStats(files, fileId, score, timeMs) {
    return files.map(file => {
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
  }

  static getQuizPreferences() {
    try {
      const defaultPrefs = {
        showTimer: true,
        showAnswersStraightaway: false,
        hideAnswerFeedback: false
      };
      const prefs = JSON.parse(localStorage.getItem('quizPreferences')) || defaultPrefs;
      
      // Handle migration from old hideAnswers to new showAnswersStraightaway
      if ('hideAnswers' in prefs) {
        prefs.showAnswersStraightaway = !prefs.hideAnswers;
        delete prefs.hideAnswers;
      }

      // Ensure all default preferences exist
      return { ...defaultPrefs, ...prefs };
    } catch (error) {
      console.error('Error loading quiz preferences:', error);
      return {
        showTimer: true,
        showAnswersStraightaway: false,
        hideAnswerFeedback: false
      };
    }
  }

  static saveQuizPreferences(preferences) {
    try {
      localStorage.setItem('quizPreferences', JSON.stringify(preferences));
      return true;
    } catch (error) {
      console.error('Error saving quiz preferences:', error);
      return false;
    }
  }
}
