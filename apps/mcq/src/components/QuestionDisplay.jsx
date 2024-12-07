import { useState, useEffect } from 'react';

export function QuestionDisplay({
  currentQuestionIndex,
  question,
  userAnswers,
  revealedQuestions,
  onOptionSelect,
  onRevealAnswers,
  selectedOptionIndex,
  showAnswersStraightaway,
  hideAnswerFeedback,
  section
}) {
  const [hiddenAnswers, setHiddenAnswers] = useState(new Set());

  // Auto-reveal choices if showAnswersStraightaway is true
  useEffect(() => {
    if (showAnswersStraightaway && !revealedQuestions.has(currentQuestionIndex)) {
      onRevealAnswers();
    }
  }, [currentQuestionIndex, showAnswersStraightaway, revealedQuestions, onRevealAnswers]);

  const toggleAnswerVisibility = (index) => {
    const newHiddenAnswers = new Set(hiddenAnswers);
    if (newHiddenAnswers.has(index)) {
      newHiddenAnswers.delete(index);
    } else {
      newHiddenAnswers.add(index);
    }
    setHiddenAnswers(newHiddenAnswers);
  };

  const renderChoices = () => {
    const isQuestionAnswered = userAnswers[currentQuestionIndex] !== undefined;

    return question.options.map((option, index) => {
      const isAnswered = userAnswers[currentQuestionIndex] !== undefined;
      const isSelected = userAnswers[currentQuestionIndex] === index;
      const isCorrect = question.correctAnswer === index;
      const isHidden = hiddenAnswers.has(index);
      const isKeyboardSelected = index === selectedOptionIndex;
      
      let className = 'option';
      // Only show correct/incorrect feedback if hideAnswerFeedback is false or we're in results section
      if (isAnswered && (!hideAnswerFeedback || section === 'results')) {
        if (isSelected) {
          className += isCorrect ? ' correct' : ' incorrect';
        } else if (isCorrect) {
          className += ' correct';
        }
      } else if (isSelected) {
        // When feedback is hidden, just highlight selected answer without indicating correctness
        className += ' selected';
      }
      
      if (isHidden) {
        className += ' greyed';
      }
      if (isKeyboardSelected) {
        className += ' keyboard-selected';
      }
      if (isQuestionAnswered && !isSelected) {
        className += ' disabled';
      }

      return (
        <div key={index} className="answer-container">
          <button
            className={className}
            onClick={() => onOptionSelect(index)}
            disabled={isQuestionAnswered}
            aria-disabled={isQuestionAnswered}
          >
            {option}
          </button>
          <button 
            className="visibility-toggle"
            onClick={() => toggleAnswerVisibility(index)}
            aria-label={isHidden ? 'Show choice' : 'Hide choice'}
          >
            <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="2">
              {isHidden ? (
                <path d="M2 2l20 20M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24M1 1l22 22M9 9l6 6" />
              ) : (
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z M12 9a3 3 0 1 1 0 6 3 3 0 0 1 0-6z" />
              )}
            </svg>
          </button>
        </div>
      );
    });
  };

  return (
    <>
      <div className="question-text">
        <div className="question-header">
          <span>{`${currentQuestionIndex + 1}. ${question.question}`}</span>
        </div>
      </div>
      
      <div className="options-container">
        {showAnswersStraightaway || revealedQuestions.has(currentQuestionIndex) ? (
          renderChoices()
        ) : (
          <div className="hidden-options clickable" onClick={onRevealAnswers}>
            <p>Click here or press Spacebar to see the possible choices</p>
          </div>
        )}
      </div>
    </>
  );
}
