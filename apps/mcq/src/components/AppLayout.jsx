import { QuizSection } from './QuizSection';
import { ResultsSection } from './ResultsSection';
import { FileList } from './FileList';

export function AppLayout({
  section,
  quizProps,
  uploadProps,
  resultsProps
}) {
  return (
    <div className="quiz-container" style={{ backgroundColor: 'var(--container-bg)' }}>
      <h1 className="app-title">Aidan's Quiz App</h1>
      
      {section === 'upload' && (
        <FileList {...uploadProps} section={section} />
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
