import { Timer } from './Timer';

export function QuizHeader({ title, currentQuestionIndex, totalQuestions, isTimerRunning, onTimerTick, showTimer }) {
  const progressPercentage = ((currentQuestionIndex + 1) / totalQuestions) * 100;

  return (
    <div className="quiz-header">
      <h2 className="quiz-title">{title}</h2>
      <div className="quiz-header-top">
        <div className="progress">
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </div>
        <Timer
          isRunning={isTimerRunning}
          onTick={onTimerTick}
          showTimer={showTimer}
        />
      </div>
      <div className="progress-bar-container">
        <div 
          className="progress-bar" 
          style={{ width: `${progressPercentage}%` }}
        />
      </div>
    </div>
  );
}
