import './ProgressBar.css';

function ProgressBar({ currentQuestion, totalQuestions }) {
  const progress = ((currentQuestion + 1) / totalQuestions) * 100;

  return (
    <div className="progress-container">
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
      <div className="progress-text">
        Question {currentQuestion + 1} of {totalQuestions}
      </div>
    </div>
  );
}

export default ProgressBar;
