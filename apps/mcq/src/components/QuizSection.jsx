import { Timer } from './Timer';
import { useState, useEffect } from 'react';

export function QuizSection({
  title,
  questions,
  currentQuestionIndex,
  userAnswers,
  revealedQuestions,
  isTimerRunning,
  onTimerTick,
  onOptionSelect,
  onRevealAnswers,
  onNextQuestion,
  onPreviousQuestion,
  onJumpToQuestion,
  onFinishQuiz,
  flaggedQuestions,
  onToggleFlag
}) {
  const [hiddenAnswers, setHiddenAnswers] = useState(new Set());
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedOptionIndex, setSelectedOptionIndex] = useState(-1);
  const currentQuestion = questions[currentQuestionIndex];
  const progressPercentage = ((currentQuestionIndex + 1) / questions.length) * 100;
  const questionsPerPage = 10;

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (!currentQuestion) return;

      switch (e.key) {
        case 'ArrowRight':
          if (currentQuestionIndex < questions.length - 1) {
            onNextQuestion();
          }
          break;
        case 'ArrowLeft':
          if (currentQuestionIndex > 0) {
            onPreviousQuestion();
          }
          break;
        case 'ArrowUp':
          if (revealedQuestions.has(currentQuestionIndex)) {
            e.preventDefault(); // Prevent page scroll when cycling through answers
            setSelectedOptionIndex(prev => {
              const newIndex = prev <= 0 ? currentQuestion.options.length - 1 : prev - 1;
              return newIndex;
            });
          }
          break;
        case 'ArrowDown':
          if (revealedQuestions.has(currentQuestionIndex)) {
            e.preventDefault(); // Prevent page scroll when cycling through answers
            setSelectedOptionIndex(prev => {
              const newIndex = prev >= currentQuestion.options.length - 1 ? 0 : prev + 1;
              return newIndex;
            });
          }
          break;
        case ' ':
          if (!revealedQuestions.has(currentQuestionIndex)) {
            e.preventDefault(); // Prevent spacebar from scrolling
            onRevealAnswers();
          }
          break;
        case 'Enter':
          if (selectedOptionIndex !== -1 && revealedQuestions.has(currentQuestionIndex)) {
            onOptionSelect(selectedOptionIndex);
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentQuestionIndex, questions.length, selectedOptionIndex, revealedQuestions, currentQuestion]);

  // Reset selected option and hidden answers when question changes
  useEffect(() => {
    setSelectedOptionIndex(-1);
    setHiddenAnswers(new Set()); // Reset hidden answers when question changes
  }, [currentQuestionIndex]);

  // Use effect to handle page synchronization with current question
  useEffect(() => {
    const newPage = Math.floor(currentQuestionIndex / questionsPerPage);
    setCurrentPage(newPage);
  }, [currentQuestionIndex, questionsPerPage]);

  const toggleAnswerVisibility = (index) => {
    const newHiddenAnswers = new Set(hiddenAnswers);
    if (newHiddenAnswers.has(index)) {
      newHiddenAnswers.delete(index);
    } else {
      newHiddenAnswers.add(index);
    }
    setHiddenAnswers(newHiddenAnswers);
  };

  const getQuestionNavClass = (index) => {
    let className = 'question-nav-btn';
    if (index === currentQuestionIndex) className += ' active';
    if (userAnswers[index] !== undefined) {
      if (userAnswers[index] === questions[index].correctAnswer) {
        className += ' correct';
      } else {
        className += ' incorrect';
      }
    }
    if (flaggedQuestions.has(index)) {
      className += ' flagged';
    }
    return className;
  };

  // Calculate total number of pages
  const totalPages = Math.ceil(questions.length / questionsPerPage);

  // Get the current page of question numbers
  const getCurrentPageQuestions = () => {
    const start = currentPage * questionsPerPage;
    const end = Math.min(start + questionsPerPage, questions.length);
    return Array.from({ length: end - start }, (_, i) => start + i);
  };

  // Handle page navigation without changing the current question
  const handlePageChange = (newPage) => {
    if (newPage >= 0 && newPage < totalPages) {
      setCurrentPage(newPage);
    }
  };

  return (
    <div className="section">
      <div className="quiz-header">
        <h2 className="quiz-title">{title}</h2>
        <div className="quiz-header-top">
          <div className="progress">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
          <Timer
            isRunning={isTimerRunning}
            onTick={onTimerTick}
          />
        </div>
        <div className="progress-bar-container">
          <div 
            className="progress-bar" 
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      <div className="question-navigation">
        <button 
          className="page-nav"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 0}
        >
          ←
        </button>
        <div>
          {getCurrentPageQuestions().map((i) => (
            <div key={i} className="question-nav-wrapper">
              <button
                className={getQuestionNavClass(i)}
                onClick={() => onJumpToQuestion(i)}
              >
                {i + 1}
              </button>
              <button 
                className="flag-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleFlag(i);
                }}
                aria-label={flaggedQuestions.has(i) ? "Unflag question" : "Flag question"}
              >
                <svg viewBox="0 0 24 24" width="12" height="12" fill={flaggedQuestions.has(i) ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
                  <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z M4 22v-7" />
                </svg>
              </button>
            </div>
          ))}
        </div>
        <button 
          className="page-nav"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages - 1}
        >
          →
        </button>
      </div>

      <div className="question-text">
        <div className="question-header">
          <span>{`${currentQuestionIndex + 1}. ${currentQuestion.question}`}</span>
          <button 
            className="flag-btn large"
            onClick={() => onToggleFlag(currentQuestionIndex)}
            aria-label={flaggedQuestions.has(currentQuestionIndex) ? "Unflag question" : "Flag question"}
          >
            <svg viewBox="0 0 24 24" width="16" height="16" fill={flaggedQuestions.has(currentQuestionIndex) ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2">
              <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z M4 22v-7" />
            </svg>
          </button>
        </div>
      </div>
      
      <div className="options-container">
        {revealedQuestions.has(currentQuestionIndex) ? (
          currentQuestion.options.map((option, index) => {
            const isAnswered = userAnswers[currentQuestionIndex] !== undefined;
            const isSelected = userAnswers[currentQuestionIndex] === index;
            const isCorrect = currentQuestion.correctAnswer === index;
            const isHidden = hiddenAnswers.has(index);
            const isKeyboardSelected = index === selectedOptionIndex;
            
            let className = 'option';
            if (isAnswered) {
              if (isSelected) {
                className += isCorrect ? ' correct' : ' incorrect';
              } else if (isCorrect) {
                className += ' correct';
              }
            }
            if (isHidden) {
              className += ' greyed';
            }
            if (isKeyboardSelected) {
              className += ' keyboard-selected';
            }

            return (
              <div key={index} className="answer-container">
                <button
                  className={className}
                  onClick={() => onOptionSelect(index)}
                >
                  {option}
                </button>
                <button 
                  className="visibility-toggle"
                  onClick={() => toggleAnswerVisibility(index)}
                  aria-label={isHidden ? 'Show answer' : 'Hide answer'}
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
          })
        ) : (
          <div className="hidden-options clickable" onClick={onRevealAnswers}>
            <p>Click here or press Spacebar to see the possible answers</p>
          </div>
        )}
      </div>

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
            disabled={currentQuestionIndex === questions.length - 1}
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
    </div>
  );
}
