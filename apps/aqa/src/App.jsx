import './App.css';
import { useState } from 'react';
import { useQuiz } from './hooks/useQuiz';
import QuizView from './components/QuizView';
import LoadingView from './components/LoadingView';
import ErrorView from './components/ErrorView';
import CompletedView from './components/CompletedView';
import QuizSelection from './components/QuizSelection';

function App() {
  const [selectedQuizId, setSelectedQuizId] = useState(null);
  
  const {
    currentQuestion,
    showExplanation,
    score,
    completed,
    answers,
    markedQuestions,
    answerStatuses,
    handleAnswer,
    handleNext,
    handlePrevious,
    handleNavigate,
    handleRestart,
    toggleMarkQuestion,
    totalQuestions,
    question,
    isMarked,
    loading,
    error,
    quiz,
    userAnswers,
    averageAnswerTime,
    setCompleted
  } = useQuiz(selectedQuizId);

  if (!selectedQuizId) {
    return (
      <div className="app-container">
        <QuizSelection onSelectQuiz={setSelectedQuizId} />
      </div>
    );
  }

  if (loading) {
    return <LoadingView />;
  }

  if (error) {
    return (
      <ErrorView 
        error={error}
        onBack={() => setSelectedQuizId(null)}
      />
    );
  }

  if (completed) {
    return (
      <CompletedView
        currentQuestion={currentQuestion}
        totalQuestions={totalQuestions}
        markedQuestions={markedQuestions}
        handleNavigate={handleNavigate}
        score={score}
        handleRestart={handleRestart}
        onSelectNew={() => setSelectedQuizId(null)}
        userAnswers={userAnswers}
        averageAnswerTime={averageAnswerTime}
        quiz={quiz}
      />
    );
  }

  return (
    <QuizView
      currentQuestion={currentQuestion}
      totalQuestions={totalQuestions}
      markedQuestions={markedQuestions}
      handleNavigate={handleNavigate}
      quiz={quiz}
      answers={answers}
      answerStatuses={answerStatuses}
      showExplanation={showExplanation}
      handleAnswer={handleAnswer}
      isMarked={isMarked}
      toggleMarkQuestion={toggleMarkQuestion}
      handlePrevious={handlePrevious}
      handleNext={handleNext}
      setCompleted={setCompleted}
    />
  );
}

export default App;
