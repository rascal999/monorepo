import { QuizSection } from './QuizSection';
import { ResultsSection } from './ResultsSection';
import { FileList } from './FileList';

export function AppLayout({
  section,
  quizProps,
  uploadProps,
  resultsProps
}) {
  // Get restartQuiz from either quizProps or resultsProps
  const handleTitleClick = () => {
    if (section === 'quiz' && quizProps.onRestart) {
      quizProps.onRestart();
    } else if (section === 'results' && resultsProps.onRestart) {
      resultsProps.onRestart();
    }
  };

  return (
    <div className="quiz-container" style={{ backgroundColor: 'var(--container-bg)' }}>
      <h1 className="app-title" onClick={handleTitleClick} style={{ cursor: 'pointer' }}>Aidan's Quiz App</h1>
      
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
