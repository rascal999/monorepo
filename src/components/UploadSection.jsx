import { useState, useEffect } from 'react';
import { FileUploader } from './FileUploader';
import { FileList } from './FileList';
import { LocalStorageManager } from '../utils/LocalStorageManager';

export function UploadSection({ onQuestionsLoaded }) {
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // Load saved files on component mount
  useEffect(() => {
    const savedFiles = LocalStorageManager.getUploadedFiles();
    const migratedFiles = savedFiles.map(file => ({
      ...file,
      stats: file.stats || LocalStorageManager.initializeStats(JSON.parse(file.content).questions)
    }));
    
    if (LocalStorageManager.saveUploadedFiles(migratedFiles)) {
      setUploadedFiles(migratedFiles);
    }
  }, []);

  // Set up global stats update function
  useEffect(() => {
    if (typeof window !== 'undefined') {
      window.updateQuizStats = (fileId, score, timeMs) => {
        const updatedFiles = LocalStorageManager.updateFileStats(uploadedFiles, fileId, score, timeMs);
        if (LocalStorageManager.saveUploadedFiles(updatedFiles)) {
          setUploadedFiles(updatedFiles);
        }
      };
    }
    return () => {
      if (typeof window !== 'undefined') {
        delete window.updateQuizStats;
      }
    };
  }, [uploadedFiles]);

  return (
    <div className="section">
      <FileUploader
        uploadedFiles={uploadedFiles}
        onFilesUpdate={setUploadedFiles}
        onQuestionsLoaded={onQuestionsLoaded}
      />
      <FileList
        files={uploadedFiles}
        onFilesUpdate={setUploadedFiles}
        onQuestionsLoaded={onQuestionsLoaded}
      />
    </div>
  );
}
