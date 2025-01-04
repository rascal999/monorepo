import { QuestionHandler } from '../utils/QuestionHandler';
import { LocalStorageManager } from '../utils/LocalStorageManager';

export function FileUploader({ uploadedFiles, onFilesUpdate, onQuestionsLoaded }) {
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
        stats: LocalStorageManager.initializeStats(loadedData.questions)
      };

      const updatedFiles = [...uploadedFiles, newFile];
      if (LocalStorageManager.saveUploadedFiles(updatedFiles)) {
        onFilesUpdate(updatedFiles);
      }

      const preferences = LocalStorageManager.getQuizPreferences();
      const preparedQuestions = QuestionHandler.prepareQuestions(loadedData.questions, preferences.randomizeQuestions);
      onQuestionsLoaded({
        title: loadedData.title,
        questions: preparedQuestions,
        fileId: newFile.id,
        preferences
      });
    } catch (error) {
      console.error('Error loading questions:', error);
      alert('Error loading questions. Please ensure your JSON file is properly formatted.');
    } finally {
      event.target.value = '';
    }
  };

  return (
    <div className="upload-section">
      <p>Upload your JSON question file (<a href="/questions/science-quiz.json" target="_blank" rel="noopener noreferrer">view sample</a>)</p>
      <input
        type="file"
        accept=".json"
        onChange={handleFileUpload}
        className="file-input"
      />
    </div>
  );
}
