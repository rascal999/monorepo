import { UploadSection } from './UploadSection';
import { QuizSection } from './QuizSection';
import { ResultsSection } from './ResultsSection';

export function AppLayout({
  section,
  quizProps,
  uploadProps,
  resultsProps
}) {
  return (
    <div className="quiz-container" style={{ backgroundColor: 'var(--container-bg)' }}>
      {section === 'upload' && (
        <UploadSection {...uploadProps} />
      )}

      {section === 'quiz' && (
        <QuizSection {...quizProps} />
      )}

      {section === 'results' && (
        <ResultsSection {...resultsProps} />
      )}
    </div>
  );
}
