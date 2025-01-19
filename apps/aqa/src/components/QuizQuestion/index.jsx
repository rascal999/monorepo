import { Formik, Form, Field } from 'formik';
import { useState, useEffect } from 'react';
import './index.css';
import './QuestionHeader.css';
import './OptionLabel.css';
import './EyeButton.css';
import './Explanation.css';

function QuizQuestion({ 
  question, 
  showExplanation, 
  answers, 
  currentQuestion, 
  onAnswer,
  isMarked,
  onToggleMark
}) {
  console.log('QuizQuestion rendered:', {
    questionId: question.id,
    currentQuestion,
    answers,
    currentAnswer: answers[currentQuestion],
    totalAnswers: answers.length,
    allAnswers: answers
  });
  const [hiddenAnswers, setHiddenAnswers] = useState(new Set());

  // Reset hidden answers when question changes
  useEffect(() => {
    setHiddenAnswers(new Set());
  }, [question.id]);

  const isAnswered = answers[currentQuestion] !== null;

  const toggleAnswerVisibility = (answerText) => {
    const newHiddenAnswers = new Set(hiddenAnswers);
    if (newHiddenAnswers.has(answerText)) {
      newHiddenAnswers.delete(answerText);
    } else {
      newHiddenAnswers.add(answerText);
    }
    setHiddenAnswers(newHiddenAnswers);
  };

  return (
    <div className="question-container">
      <div className="question-header">
        <p className="question">{question.question_text}</p>
        <button 
          className={`control-button ${isMarked ? 'marked' : ''}`}
          onClick={onToggleMark}
          title={isMarked ? 'Remove mark' : 'Mark for review'}
        >
          <span className="control-icon">★</span>
        </button>
      </div>

      <div className="options">
        {question.answers.map((answer) => (
          <div key={answer.id} className="option-wrapper">
            <label 
              className={`option-label ${
                showExplanation
                  ? answer.is_correct
                    ? 'correct'
                    : answer.answer_text === answers[currentQuestion]
                      ? 'incorrect'
                      : 'disabled'
                  : ''
              } ${hiddenAnswers.has(answer.answer_text) ? 'hidden-answer' : ''}`}
            >
              <input
                type="radio"
                name={`question-${question.id}-${currentQuestion}`}
                value={answer.answer_text}
                checked={answers[currentQuestion] === answer.answer_text}
                onChange={() => {
                  if (!showExplanation && !hiddenAnswers.has(answer.answer_text)) {
                    console.log('Answer selected:', {
                      answerText: answer.answer_text,
                      currentQuestion,
                      isCorrect: answer.is_correct,
                      previousAnswer: answers[currentQuestion],
                      allAnswers: answers
                    });
                    onAnswer(answer.answer_text);
                  }
                }}
                disabled={showExplanation || hiddenAnswers.has(answer.answer_text)}
              />
              <span className="option-text">{answer.answer_text}</span>
            </label>
            {!isAnswered && (
              <button 
                type="button"
                className={`eye-button ${hiddenAnswers.has(answer.answer_text) ? 'hidden' : ''}`}
                onClick={() => toggleAnswerVisibility(answer.answer_text)}
                title={hiddenAnswers.has(answer.answer_text) ? 'Show answer' : 'Hide answer'}
              >
                <span className="eye-icon">👁</span>
              </button>
            )}
          </div>
        ))}
      </div>

      {showExplanation && (
        <div className="explanation">
          <p>{question.explanation}</p>
        </div>
      )}
    </div>
  );
}

export default QuizQuestion;
