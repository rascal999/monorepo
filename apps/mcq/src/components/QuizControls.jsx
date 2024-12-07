export function QuizControls({
  currentQuestionIndex,
  totalQuestions,
  onPreviousQuestion,
  onNextQuestion,
  onFinishQuiz
}) {
  return (
    <div className="quiz-controls">
      <div className="navigation-controls">
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

        <button 
          onClick={onFinishQuiz}
          className="finish-btn"
        >
          Finish Quiz
        </button>
      </div>
    </div>
  );
}
