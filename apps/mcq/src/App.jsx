import { useState, useEffect, useCallback } from 'react';
import { UploadSection } from './components/UploadSection';
import { QuizSection } from './components/QuizSection';
import { ResultsSection } from './components/ResultsSection';
import './styles/index.css';

function App() {
  const [section, setSection] = useState('upload');
  const [title, setTitle] = useState('');
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [userAnswers, setUserAnswers] = useState([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [showAnswers, setShowAnswers] = useState(false);
  const [revealedQuestions, setRevealedQuestions] = useState(new Set());
  const [questionStartTime, setQuestionStartTime] = useState(0);
  const [questionTimes, setQuestionTimes] = useState([]);
  const [currentFileId, setCurrentFileId] = useState(null);
  const [flaggedQuestions, setFlaggedQuestions] = useState(new Set());
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('theme');
    return savedTheme || 'light';
  });

  useEffect(() => {
    document.querySelector('html').setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'light' ? 'dark' : 'light');
  };

  const toggleQuestionFlag = useCallback((index) => {
    setFlaggedQuestions(prev => {
      const newFlags = new Set(prev);
      if (newFlags.has(index)) {
        newFlags.delete(index);
      } else {
        newFlags.add(index);
      }
      return newFlags;
    });
  }, []);

  const startQuiz = useCallback((quizData) => {
    try {
      setTitle(quizData.title);
      setQuestions(quizData.questions);
      setCurrentQuestionIndex(0);
      setScore(0);
      setUserAnswers([]);
      setElapsedTime(0);
      setSection('quiz');
      setIsTimerRunning(true);
      setShowAnswers(false);
      setRevealedQuestions(new Set());
      setQuestionTimes([]);
      setQuestionStartTime(Date.now());
      setCurrentFileId(quizData.fileId);
      setFlaggedQuestions(new Set());
    } catch (error) {
      console.error('Error starting quiz:', error);
      alert('Error starting quiz. Please try again.');
    }
  }, []);

  const handleOptionSelect = useCallback((selectedIndex) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion) return;

    setUserAnswers(prev => {
      const newAnswers = [...prev];
      newAnswers[currentQuestionIndex] = selectedIndex;
      return newAnswers;
    });

    if (selectedIndex === currentQuestion.correctAnswer) {
      setScore(prev => prev + 1);
    }
  }, [currentQuestionIndex, questions]);

  const handleRevealAnswers = useCallback(() => {
    setRevealedQuestions(prev => new Set([...prev, currentQuestionIndex]));
  }, [currentQuestionIndex]);

  const recordQuestionTime = useCallback(() => {
    const timeTaken = Date.now() - questionStartTime;
    setQuestionTimes(prev => [...prev, timeTaken]);
    setQuestionStartTime(Date.now());
  }, [questionStartTime]);

  const handleNextQuestion = useCallback(() => {
    if (currentQuestionIndex < questions.length - 1) {
      recordQuestionTime();
      setCurrentQuestionIndex(prev => prev + 1);
    }
  }, [currentQuestionIndex, questions.length, recordQuestionTime]);

  const handlePreviousQuestion = useCallback(() => {
    if (currentQuestionIndex > 0) {
      recordQuestionTime();
      setCurrentQuestionIndex(prev => prev - 1);
    }
  }, [currentQuestionIndex, recordQuestionTime]);

  const handleJumpToQuestion = useCallback((index) => {
    if (index >= 0 && index < questions.length) {
      recordQuestionTime();
      setCurrentQuestionIndex(index);
    }
  }, [questions.length, recordQuestionTime]);

  const finishQuiz = useCallback(() => {
    try {
      const finalElapsedTime = elapsedTime;
      setIsTimerRunning(false);
      setSection('results');
      setElapsedTime(finalElapsedTime);
      
      if (currentFileId && window.updateQuizStats) {
        window.updateQuizStats(currentFileId, score, finalElapsedTime);
      }
    } catch (error) {
      console.error('Error finishing quiz:', error);
    }
  }, [currentFileId, elapsedTime, score]);

  const handleTimerTick = useCallback((time) => {
    setElapsedTime(time);
  }, []);

  const restartQuiz = useCallback(() => {
    try {
      setSection('upload');
      setTitle('');
      setIsTimerRunning(false);
      setElapsedTime(0);
      setShowAnswers(false);
      setRevealedQuestions(new Set());
      setQuestionTimes([]);
      setCurrentFileId(null);
      setFlaggedQuestions(new Set());
    } catch (error) {
      console.error('Error restarting quiz:', error);
    }
  }, []);

  return (
    <div className="app">
      <button 
        className="theme-toggle" 
        onClick={toggleTheme}
        aria-label="Toggle dark mode"
      >
        {theme === 'light' ? '🌙' : '☀️'}
      </button>
      <div className="container">
        {section === 'upload' && (
          <UploadSection onQuestionsLoaded={startQuiz} />
        )}

        {section === 'quiz' && (
          <QuizSection
            title={title}
            questions={questions}
            currentQuestionIndex={currentQuestionIndex}
            userAnswers={userAnswers}
            revealedQuestions={revealedQuestions}
            isTimerRunning={isTimerRunning}
            onTimerTick={handleTimerTick}
            onOptionSelect={handleOptionSelect}
            onRevealAnswers={handleRevealAnswers}
            onNextQuestion={handleNextQuestion}
            onPreviousQuestion={handlePreviousQuestion}
            onJumpToQuestion={handleJumpToQuestion}
            onFinishQuiz={finishQuiz}
            flaggedQuestions={flaggedQuestions}
            onToggleFlag={toggleQuestionFlag}
          />
        )}

        {section === 'results' && (
          <ResultsSection
            title={title}
            questions={questions}
            score={score}
            elapsedTime={elapsedTime}
            showAnswers={showAnswers}
            userAnswers={userAnswers}
            questionTimes={questionTimes}
            onToggleAnswers={() => setShowAnswers(!showAnswers)}
            onRestart={restartQuiz}
          />
        )}
      </div>
    </div>
  );
}

export default App;
