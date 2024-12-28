import { useState } from 'react';
import { ThemeProvider } from './components/ThemeProvider';
import { AppLayout } from './components/AppLayout';
import { useQuizState } from './hooks/useQuizState';
import { useQuizStats } from './hooks/useQuizStats';
import './styles/index.css';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const quizState = useQuizState();
  useQuizStats(uploadedFiles, setUploadedFiles);

  const uploadProps = {
    uploadedFiles,
    onFilesUpdate: setUploadedFiles,
    onQuestionsLoaded: quizState.startQuiz
  };

  const quizProps = {
    title: quizState.title,
    questions: quizState.questions,
    currentQuestionIndex: quizState.currentQuestionIndex,
    userAnswers: quizState.userAnswers,
    revealedQuestions: quizState.revealedQuestions,
    isTimerRunning: quizState.isTimerRunning,
    onTimerTick: quizState.handleTimerTick,
    onOptionSelect: quizState.handleOptionSelect,
    onRevealAnswers: quizState.handleRevealAnswers,
    onNextQuestion: quizState.handleNextQuestion,
    onPreviousQuestion: quizState.handlePreviousQuestion,
    onJumpToQuestion: quizState.handleJumpToQuestion,
    onFinishQuiz: quizState.finishQuiz,
    flaggedQuestions: quizState.flaggedQuestions,
    onToggleFlag: quizState.toggleQuestionFlag,
    showTimer: quizState.showTimer,
    showAnswersStraightaway: quizState.showAnswersStraightaway,
    hideAnswerFeedback: quizState.hideAnswerFeedback,
    section: quizState.section,
    onRestart: quizState.restartQuiz
  };

  const resultsProps = {
    title: quizState.title,
    questions: quizState.questions,
    score: quizState.score,
    elapsedTime: quizState.elapsedTime,
    showAnswers: quizState.showAnswers,
    userAnswers: quizState.userAnswers,
    questionTimes: quizState.questionTimes,
    onToggleAnswers: () => quizState.setShowAnswers(!quizState.showAnswers),
    onRestart: quizState.restartQuiz
  };

  return (
    <div className="app">
      <ThemeProvider>
        <AppLayout
          section={quizState.section}
          uploadProps={uploadProps}
          quizProps={quizProps}
          resultsProps={resultsProps}
        />
      </ThemeProvider>
    </div>
  );
}

export default App;
