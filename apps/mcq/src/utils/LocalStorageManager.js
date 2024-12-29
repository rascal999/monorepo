export class LocalStorageManager {
  static async loadQuestionsFromDirectory() {
    try {
      const files = await this.recursivelyLoadFiles('/questions');
      return files.filter(file => file !== null);
    } catch (error) {
      console.error('Error loading questions from directory:', error);
      return [];
    }
  }

  static async recursivelyLoadFiles(path) {
    try {
      // Get list of files from directory
      const response = await fetch(path);
      const html = await response.text();
      
      // Parse the directory listing HTML to get file and directory names
      const entries = html.match(/href="([^"]+)"/g)
        ?.map(href => href.match(/href="([^"]+)"/)[1])
        ?.filter(name => name !== '../') || [];

      // Process all entries (files and directories)
      const results = await Promise.all(
        entries.map(async entry => {
          // Remove any leading slashes from entry
          const cleanEntry = entry.startsWith('/') ? entry.slice(1) : entry;
          // Ensure path ends with slash if it doesn't already
          const basePath = path.endsWith('/') ? path : `${path}/`;
          const fullPath = `${basePath}${cleanEntry}`;
          
          if (entry.endsWith('/')) {
            // It's a directory, recursively load its contents
            return this.recursivelyLoadFiles(fullPath.slice(0, -1)); // Remove trailing slash for fetch
          } else if (entry.endsWith('.json')) {
            // It's a JSON file, load its content
            try {
              const fileResponse = await fetch(fullPath);
              const content = await fileResponse.json();
              
              // Create ID from path, removing leading '/questions' and trailing '.json'
              const id = fullPath
                .replace(/^\/questions\/?/, '') // Remove leading /questions/ or /questions
                .replace(/^\//, '') // Remove any remaining leading slash
                .replace(/\.json$/, ''); // Remove .json extension
              
              return {
                id,
                title: content.title || id.split('/').pop(), // Use last part of path if no title
                content: JSON.stringify(content),
                timestamp: new Date().getTime(),
                stats: this.initializeStats(content.questions)
              };
            } catch (error) {
              console.error(`Error loading file ${fullPath}:`, error);
              return null;
            }
          }
          return null;
        })
      );

      // Flatten the results array since recursive calls return arrays
      return results.flat().filter(result => result !== null);
    } catch (error) {
      console.error('Error in recursive file loading:', error);
      return [];
    }
  }

  static getUploadedFiles() {
    try {
      const savedFiles = JSON.parse(localStorage.getItem('uploadedFiles') || '[]');
      return savedFiles;
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
        hideAnswerFeedback: false,
        randomizeQuestions: true
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
        hideAnswerFeedback: false,
        randomizeQuestions: true
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
