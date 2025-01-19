import './CompletionScreen.css';

function CompletionScreen({ score, totalQuestions, onRestart }) {
  return (
    <div className="completion-screen">
      <h1>Quiz Completed!</h1>
      <p className="final-score">Your score: {score} out of {totalQuestions}</p>
      <button onClick={onRestart} className="restart-button">
        Restart Quiz
      </button>
    </div>
  );
}

export default CompletionScreen;
