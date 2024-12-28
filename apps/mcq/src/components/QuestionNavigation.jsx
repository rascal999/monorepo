import { useState, useEffect, useCallback } from 'react';

export function QuestionNavigation({
  currentQuestionIndex,
  totalQuestions,
  userAnswers,
  questions,
  flaggedQuestions,
  onJumpToQuestion,
  onToggleFlag,
  hideAnswerFeedback,
  section
}) {
  const [questionsPerPage, setQuestionsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(0);
  
  // Update questions per page based on screen size
  const updateQuestionsPerPage = useCallback(() => {
    const isMobile = window.innerWidth <= 600;
    const newQuestionsPerPage = isMobile ? 5 : 10;
    if (newQuestionsPerPage !== questionsPerPage) {
      // Recalculate current page to maintain approximate scroll position
      const currentFirstQuestion = currentPage * questionsPerPage;
      const newPage = Math.floor(currentFirstQuestion / newQuestionsPerPage);
      setQuestionsPerPage(newQuestionsPerPage);
      setCurrentPage(newPage);
    }
  }, [questionsPerPage, currentPage]);

  useEffect(() => {
    updateQuestionsPerPage();
    window.addEventListener('resize', updateQuestionsPerPage);
    return () => window.removeEventListener('resize', updateQuestionsPerPage);
  }, [updateQuestionsPerPage]);

  const totalPages = Math.ceil(totalQuestions / questionsPerPage);

  // Update page when current question changes
  useEffect(() => {
    const targetPage = Math.floor(currentQuestionIndex / questionsPerPage);
    if (targetPage !== currentPage) {
      setCurrentPage(targetPage);
    }
  }, [currentQuestionIndex, questionsPerPage]);

  const getQuestionNavClass = (index) => {
    let className = 'question-nav-btn';
    if (index === currentQuestionIndex) className += ' active';
    
    // Only show correct/incorrect when hideAnswerFeedback is false or we're in results
    if (userAnswers[index] !== undefined) {
      if (!hideAnswerFeedback || section === 'results') {
        if (userAnswers[index] === questions[index].correctAnswer) {
          className += ' correct';
        } else {
          className += ' incorrect';
        }
      } else {
        // When feedback is hidden, just show as answered
        className += ' answered';
      }
    }
    
    if (flaggedQuestions.has(index)) {
      className += ' flagged';
    }
    return className;
  };

  const getCurrentPageQuestions = () => {
    const start = currentPage * questionsPerPage;
    const end = Math.min(start + questionsPerPage, totalQuestions);
    return Array.from({ length: end - start }, (_, i) => start + i);
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 0 && newPage < totalPages) {
      setCurrentPage(newPage);
      // Jump to first question of the new page
      onJumpToQuestion(newPage * questionsPerPage);
    }
  };

  return (
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
  );
}
