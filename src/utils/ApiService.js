import axios from 'axios';

const API_URL = 'http://localhost:3001/api';

export class ApiService {
  static async getCategories() {
    try {
      const response = await axios.get(`${API_URL}/categories`);
      return response.data.map(category => ({
        id: category.slug,
        title: category.name,
        content: JSON.stringify({
          title: category.name,
          questions: [] // Will be populated when loaded
        }),
        timestamp: new Date().getTime()
      }));
    } catch (error) {
      console.error('Error fetching categories:', error);
      throw error;
    }
  }

  static async getCategoryQuestions(slug) {
    try {
      const response = await axios.get(`${API_URL}/categories/${slug}/questions`);
      const questions = response.data.map(q => ({
        question: q.question_text,
        options: q.options.map(opt => opt.text),
        correctAnswer: q.options.findIndex(opt => opt.is_correct === true)
      }));

      return {
        title: slug.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' '),
        questions
      };
    } catch (error) {
      console.error('Error fetching questions:', error);
      throw error;
    }
  }

  static async getQuestion(id) {
    try {
      const response = await axios.get(`${API_URL}/questions/${id}`);
      const q = response.data;
      return {
        question: q.question_text,
        options: q.options.map(opt => opt.text),
        correctAnswer: q.options.findIndex(opt => opt.is_correct === true)
      };
    } catch (error) {
      console.error('Error fetching question:', error);
      throw error;
    }
  }
}
