import { useQuizState } from './useQuizState';
import { useQuizHandlers } from './useQuizHandlers';
import { useQuizEffects } from './useQuizEffects';

export function useQuiz(quizId) {
  const state = useQuizState(quizId);
  const handlers = useQuizHandlers(state);
  useQuizEffects(state, handlers);

  // Return loading/error states after hooks are called
  if (state.loading || state.error) {
    return state;
  }

  return {
    ...state,
    ...handlers
  };
}
