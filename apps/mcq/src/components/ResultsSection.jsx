export function ResultsSection({
  title,
  questions,
  score,
  elapsedTime,
  showAnswers,
  userAnswers,
  questionTimes,
  onToggleAnswers,
  onRestart
}) {
  const formatTime = (ms) => {
    if (!ms && ms !== 0) return "0m 0s";
    const totalSeconds = Math.floor(ms / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${minutes}m ${seconds}s`;
  };

  const calculateStats = () => {
    const totalQuestions = questions.length;
    const correctAnswers = score;
    const incorrectAnswers = totalQuestions - correctAnswers;
    const accuracy = ((correctAnswers / totalQuestions) * 100).toFixed(1);
    const averageTimePerQuestion = elapsedTime / totalQuestions;
    
    return {
      totalQuestions,
      correctAnswers,
      incorrectAnswers,
      accuracy,
      averageTimePerQuestion
    };
  };

  const stats = calculateStats();

  return (
    <div className="section">
      <h2>Quiz Complete!</h2>
      <h3 className="quiz-title">{title}</h3>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Score</div>
          <div className="stat-value">{stats.accuracy}%</div>
          <div className="stat-detail">
            {stats.correctAnswers} of {stats.totalQuestions} correct
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Time</div>
          <div className="stat-value">{formatTime(elapsedTime)}</div>
          <div className="stat-detail">
            ~{formatTime(stats.averageTimePerQuestion)} per question
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Questions</div>
          <div className="stat-value">{stats.totalQuestions}</div>
          <div className="stat-detail">
            {stats.correctAnswers} ✓ | {stats.incorrectAnswers} ✗
          </div>
        </div>
      </div>

      <div className="answers-controls">
        <button onClick={onToggleAnswers}>
          {showAnswers ? 'Hide Answers' : 'Show Answers'}
        </button>
        <button onClick={onRestart}>Start New Quiz</button>
      </div>

      {showAnswers && (
        <div className="answers-summary">
          <h3>Questions Summary:</h3>
          {questions.map((q, index) => {
            const userAnswer = userAnswers[index];
            const isAnswered = userAnswer !== undefined && userAnswer !== null;
            const isCorrect = isAnswered && userAnswer === q.correctAnswer;
            return (
              <div
                key={index}
                className={`question-summary ${isAnswered ? (isCorrect ? 'correct' : 'incorrect') : 'incorrect'}`}
              >
                <div className="question-header">
                  <p className="question-text">
                    <strong>Q{index + 1}:</strong> {q.question}
                  </p>
                  <div className="question-stats">
                    <span className={`status-badge ${isAnswered ? (isCorrect ? 'correct' : 'incorrect') : 'incorrect'}`}>
                      {isAnswered ? (isCorrect ? '✓ Correct' : '✗ Incorrect') : '- Not Answered'}
                    </span>
                    <span className="time-badge">
                      {formatTime(questionTimes[index])}
                    </span>
                  </div>
                </div>
                
                <div className="options-summary">
                  {q.options.map((option, optIndex) => {
                    const isUserAnswer = optIndex === userAnswer;
                    const isCorrectAnswer = optIndex === q.correctAnswer;
                    let optionClass = 'option-summary';
                    if (isUserAnswer) optionClass += ' user-answer';
                    if (isCorrectAnswer) optionClass += ' correct-answer';
                    
                    return (
                      <div key={optIndex} className={optionClass}>
                        {option}
                        {isUserAnswer && (
                          <span className="answer-indicator">
                            {isCorrect ? '✓' : '✗'}
                          </span>
                        )}
                        {isCorrectAnswer && !isUserAnswer && (
                          <span className="answer-indicator correct">✓</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
