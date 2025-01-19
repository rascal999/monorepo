const API_BASE_URL = 'http://localhost:3001/api';

export const getQuizzes = async () => {
  const response = await fetch(`${API_BASE_URL}/quizzes`);
  if (!response.ok) {
    throw new Error('Failed to fetch quizzes');
  }
  return response.json();
};

export const getQuizById = async (id) => {
  const response = await fetch(`${API_BASE_URL}/quizzes/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch quiz');
  }
  return response.json();
};

export const createQuiz = async (quizData) => {
  const response = await fetch(`${API_BASE_URL}/quizzes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(quizData),
  });
  if (!response.ok) {
    throw new Error('Failed to create quiz');
  }
  return response.json();
};
