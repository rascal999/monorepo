import { useEffect } from 'react';
import { LocalStorageManager } from '../utils/LocalStorageManager';

export function useQuizStats(uploadedFiles, setUploadedFiles) {
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
  }, [uploadedFiles, setUploadedFiles]);

  useEffect(() => {
    const savedFiles = LocalStorageManager.getUploadedFiles();
    const migratedFiles = savedFiles.map(file => ({
      ...file,
      stats: file.stats || LocalStorageManager.initializeStats(JSON.parse(file.content).questions)
    }));
    
    if (LocalStorageManager.saveUploadedFiles(migratedFiles)) {
      setUploadedFiles(migratedFiles);
    }
  }, [setUploadedFiles]);
}
