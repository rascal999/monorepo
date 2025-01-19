import express from 'express';
import cors from 'cors';
import { initDb, getQuizzes, getQuizById, createQuiz } from './db.js';

const app = express();
const port = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

// Initialize database
initDb().then(() => {
  console.log('Database initialized');

  // Sample quiz data
  const sampleQuiz = {
    title: 'JavaScript Fundamentals',
    questions: [
      {
        question_text: 'What is the output of typeof null?',
        explanation: 'While null is a primitive value in JavaScript, typeof null returns "object". This is a known quirk in JavaScript that has persisted for historical reasons.',
        answers: [
          { answer_text: '"object"', is_correct: true },
          { answer_text: '"null"', is_correct: false },
          { answer_text: '"undefined"', is_correct: false },
          { answer_text: 'null', is_correct: false }
        ]
      },
      {
        question_text: 'What is closure in JavaScript?',
        explanation: 'A closure is a function that has access to variables in its outer (enclosing) lexical scope, even after the outer function has returned.',
        answers: [
          { answer_text: 'A function that has access to variables in its outer scope', is_correct: true },
          { answer_text: 'A way to close a function', is_correct: false },
          { answer_text: 'A method to end a loop', is_correct: false },
          { answer_text: 'A type of JavaScript object', is_correct: false }
        ]
      },
      {
        question_text: 'What is the difference between == and === in JavaScript?',
        explanation: 'The == operator performs type coercion before comparison, while === compares both value and type without coercion.',
        answers: [
          { answer_text: '== compares values with type coercion, === compares values and types', is_correct: true },
          { answer_text: 'They are exactly the same', is_correct: false },
          { answer_text: '=== is just a syntax error', is_correct: false },
          { answer_text: '== is used for numbers, === is used for strings', is_correct: false }
        ]
      }
    ]
  };

  // Create sample quiz if no quizzes exist
  getQuizzes().then(quizzes => {
    if (quizzes.length === 0) {
      createQuiz(sampleQuiz.title, sampleQuiz.questions)
        .then(() => console.log('Sample quiz created'))
        .catch(console.error);
    }
  });
});

// Get all quizzes
app.get('/api/quizzes', async (req, res) => {
  try {
    const quizzes = await getQuizzes();
    res.json(quizzes);
  } catch (error) {
    console.error('Error getting quizzes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get quiz by ID
app.get('/api/quizzes/:id', async (req, res) => {
  try {
    const quiz = await getQuizById(req.params.id);
    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }
    res.json(quiz);
  } catch (error) {
    console.error('Error getting quiz:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Create new quiz
app.post('/api/quizzes', async (req, res) => {
  try {
    const { title, questions } = req.body;
    if (!title || !questions || !Array.isArray(questions) || questions.length === 0) {
      return res.status(400).json({ error: 'Invalid quiz data' });
    }

    const quizId = await createQuiz(title, questions);
    res.status(201).json({ id: quizId });
  } catch (error) {
    console.error('Error creating quiz:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
