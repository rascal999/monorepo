import { useState } from 'react';
import './styles.css';

function NavigationButtons({ 
  onPrevious, 
  onNext, 
  isFirstQuestion, 
  isLastQuestion,
  onFinish,
  answers,
  totalQuestions
}) {
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const allQuestionsAnswered = answers && answers.every(answer => answer !== null);

  const handleFinishClick = () => {
    if (!allQuestionsAnswered) {
      alert('Please answer all questions before finishing the quiz.');
      return;
    }
    setShowConfirmModal(true);
  };

  const handleConfirmFinish = () => {
    setShowConfirmModal(false);
    onFinish();
  };

  return (
    <>
      <div className="navigation-buttons">
        <button 
          onClick={onPrevious} 
          className="nav-button"
          disabled={isFirstQuestion}
        >
          Previous
        </button>
        <button 
          onClick={handleFinishClick}
          className="finish-button"
          disabled={!allQuestionsAnswered}
        >
          Finish Quiz
        </button>
        <button 
          onClick={onNext} 
          className="nav-button"
          disabled={isLastQuestion}
        >
          Next
        </button>
      </div>

      {showConfirmModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3 className="modal-title">Are you sure you want to finish the quiz early?</h3>
            <div className="modal-buttons">
              <button 
                className="modal-button cancel"
                onClick={() => setShowConfirmModal(false)}
              >
                Cancel
              </button>
              <button 
                className="modal-button confirm"
                onClick={handleConfirmFinish}
              >
                Finish Quiz
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default NavigationButtons;
