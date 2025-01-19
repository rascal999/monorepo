import './NavigationDots.css';

function NavigationDots({ 
  totalQuestions, 
  currentQuestion, 
  answers,
  answerStatuses,
  markedQuestions,
  onNavigate 
}) {
  return (
    <div className="navigation-dots">
      {Array.from({ length: totalQuestions }, (_, index) => (
        <button
          key={index}
          className={`nav-dot ${index === currentQuestion ? 'active' : ''} ${
            answerStatuses[index] ? answerStatuses[index] : ''
          } ${markedQuestions[index] ? 'marked' : ''}`}
          onClick={() => onNavigate(index)}
          title={`Question ${index + 1}${markedQuestions[index] ? ' (Marked for review)' : ''}`}
        >
          {index + 1}
          {markedQuestions[index] && <span className="mark-indicator">★</span>}
        </button>
      ))}
    </div>
  );
}

export default NavigationDots;
