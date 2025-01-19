import { useEffect } from 'react';

export function useQuizEffects(state, handlers) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Don't handle navigation when typing
      if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
        return;
      }
      
      switch (event.key) {
        case 'ArrowLeft':
          if (state.currentQuestion > 0) {
            event.preventDefault();
            handlers.handleNavigate(state.currentQuestion - 1);
          }
          break;
        case 'ArrowRight':
          if (state.currentQuestion < state.totalQuestions - 1) {
            event.preventDefault();
            handlers.handleNavigate(state.currentQuestion + 1);
          }
          break;
        default:
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    state.currentQuestion,
    state.totalQuestions,
    handlers.handleNavigate
  ]);
}
