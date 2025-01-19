const API_BASE_URL = 'http://localhost:3001/api';

const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.details || errorData.error || response.statusText);
  }
  return response.json();
}

export const getQuizzes = async () => {
  const response = await fetch(`${API_BASE_URL}/quizzes`, defaultOptions);
  return handleResponse(response);
};

export const getQuizById = async (id) => {
  const response = await fetch(`${API_BASE_URL}/quizzes/${id}`, defaultOptions);
  return handleResponse(response);
};

export const createQuiz = async (quizData) => {
  const response = await fetch(`${API_BASE_URL}/quizzes`, {
    ...defaultOptions,
    method: 'POST',
    body: JSON.stringify(quizData)
  });
  return handleResponse(response);
};

export const generateQuiz = async (topic) => {
  const response = await fetch(`${API_BASE_URL}/generate-quiz`, {
    ...defaultOptions,
    method: 'POST',
    body: JSON.stringify({ topic })
  });
  return handleResponse(response);
};

export const deleteQuiz = async (id) => {
  const response = await fetch(`${API_BASE_URL}/quizzes/${id}`, {
    ...defaultOptions,
    method: 'DELETE'
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.details || errorData.error || response.statusText);
  }
  return true;
};

export const generateQuizFromFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/generate-quiz-from-file`, {
    method: 'POST',
    body: formData
  });
  return handleResponse(response);
};
