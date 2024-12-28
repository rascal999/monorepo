export function QuizControls({
  currentQuestionIndex,
  totalQuestions,
  onPreviousQuestion,
  onNextQuestion,
  onFinishQuiz
}) {
  return (
    <div className="quiz-controls">
      <div className="navigation-controls vertical">
        <div className="nav-row">
          <button 
            onClick={onPreviousQuestion} 
            className="nav-btn"
            disabled={currentQuestionIndex === 0}
          >
            Previous
          </button>
          
          <button 
            onClick={onNextQuestion} 
            className="nav-btn"
            disabled={currentQuestionIndex === totalQuestions - 1}
          >
            Next
          </button>
        </div>

        <button 
          onClick={onFinishQuiz}
          className="finish-btn nav-btn"
        >
          Finish Quiz
        </button>
      </div>
    </div>
  );
}
