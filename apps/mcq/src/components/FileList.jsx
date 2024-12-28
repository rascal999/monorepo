import { useState, useEffect } from 'react';
import { QuestionHandler } from '../utils/QuestionHandler';
import { LocalStorageManager } from '../utils/LocalStorageManager';
import { UploadSection } from './UploadSection';
import { QuizOptions } from './QuizOptions';
import { QuizListSection } from './QuizListSection';

export function FileList({ files, onFilesUpdate, onQuestionsLoaded, uploadedFiles, section }) {
  const [preferences, setPreferences] = useState(LocalStorageManager.getQuizPreferences());
  const [allFiles, setAllFiles] = useState([]);
  const [directoryFiles, setDirectoryFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [uploadedCurrentPage, setUploadedCurrentPage] = useState(1);
  const [availableCurrentPage, setAvailableCurrentPage] = useState(1);
  const itemsPerPage = 10;

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

        // Sort files alphabetically by title
        const sortedFiles = mergedFiles.sort((a, b) => a.title.localeCompare(b.title));
        setAllFiles(sortedFiles);
        onFilesUpdate(sortedFiles);
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
  }, []);

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

  const filterFiles = (files) => {
    return files.filter(file => 
      file.title.toLowerCase().includes(searchTerm.toLowerCase())
    );
  };

  if (isLoading) {
    return <div className="loading">Loading quizzes...</div>;
  }

  if (allFiles.length === 0) {
    return null;
  }

  // Only render quiz sections if we're in the upload section
  if (section !== 'upload') {
    return null;
  }

  const uploadedQuizzes = filterFiles(allFiles.filter(file => !directoryFiles.some(df => df.id === file.id)));
  const availableQuizzes = filterFiles(allFiles.filter(file => directoryFiles.some(df => df.id === file.id)));

  return (
    <div className="quiz-sections">
      {uploadedQuizzes.length > 0 && (
        <QuizListSection
          title="My Uploaded Quizzes"
          files={uploadedQuizzes}
          isDirectoryFiles={false}
          onLoad={handleLoad}
          onDelete={handleDelete}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          currentPage={uploadedCurrentPage}
          onPageChange={setUploadedCurrentPage}
          itemsPerPage={itemsPerPage}
        />
      )}

      {availableQuizzes.length > 0 && (
        <QuizListSection
          title="Available Quizzes"
          files={availableQuizzes}
          isDirectoryFiles={true}
          onLoad={handleLoad}
          onDelete={handleDelete}
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          currentPage={availableCurrentPage}
          onPageChange={setAvailableCurrentPage}
          itemsPerPage={itemsPerPage}
        />
      )}

      <div className="quiz-section">
        <h2 className="section-title">Upload Your Quiz</h2>
        <UploadSection 
          uploadedFiles={uploadedFiles || files}
          onFilesUpdate={onFilesUpdate}
          onQuestionsLoaded={onQuestionsLoaded}
        />
      </div>

      <QuizOptions
        preferences={preferences}
        onPreferencesChange={setPreferences}
      />
    </div>
  );
}
