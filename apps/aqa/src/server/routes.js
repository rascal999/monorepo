import express from 'express';
import multer from 'multer';
import { getQuizzes, getQuizById, createQuiz, deleteQuiz } from './db.js';
import { generateQuiz, generateQuizFromContent, fixQuizData } from './openrouter/index.js';

const router = express.Router();
const upload = multer();

// Get all quizzes
router.get('/quizzes', async (req, res) => {
  try {
    const quizzes = await getQuizzes();
    res.json(quizzes);
  } catch (error) {
    console.error('Error getting quizzes:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get quiz by ID
router.get('/quizzes/:id', async (req, res) => {
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
router.post('/quizzes', async (req, res) => {
  try {
    const { title, questions, keywords } = req.body;
    if (!title || !questions || !Array.isArray(questions) || questions.length === 0) {
      return res.status(400).json({ error: 'Invalid quiz data' });
    }

    const quizId = await createQuiz(title, questions, keywords || []);
    res.status(201).json({ id: quizId });
  } catch (error) {
    console.error('Error creating quiz:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Generate quiz using AI
router.post('/generate-quiz', async (req, res) => {
  try {
    const { topic } = req.body;
    if (!topic) {
      return res.status(400).json({ error: 'Topic is required' });
    }

    console.log('Generating quiz for topic:', topic);
    let quizData = await generateQuiz(topic);

    // Try to fix any issues with the generated data
    try {
      quizData = fixQuizData(quizData);
    } catch (fixError) {
      console.error('Failed to fix quiz data:', fixError);
      // Continue with original data if fix fails
    }

    const quizId = await createQuiz(quizData.title, quizData.questions, quizData.keywords || []);
    console.log('Quiz generated and saved with ID:', quizId);
    
    res.status(201).json({ id: quizId });
  } catch (error) {
    console.error('Error generating quiz:', {
      topic: req.body.topic,
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    });
    res.status(500).json({ 
      error: 'Failed to generate quiz',
      details: error.message 
    });
  }
});

// Generate quiz from uploaded file
// Delete quiz by ID
router.delete('/quizzes/:id', async (req, res) => {
  try {
    const quiz = await getQuizById(req.params.id);
    if (!quiz) {
      return res.status(404).json({ error: 'Quiz not found' });
    }
    await deleteQuiz(req.params.id);
    res.status(204).send();
  } catch (error) {
    console.error('Error deleting quiz:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

router.post('/generate-quiz-from-file', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    // Log file details
    console.log('File upload details:', {
      originalname: req.file.originalname,
      mimetype: req.file.mimetype,
      size: req.file.size
    });

    // Convert file buffer to text
    const fileContent = req.file.buffer.toString('utf-8');
    console.log('File content length:', fileContent.length);
    console.log('First 200 characters of content:', fileContent.substring(0, 200));
    console.log('Generating quiz from file content');
    
    console.log('Calling generateQuizFromContent...');
    let quizData = await generateQuizFromContent(fileContent);
    console.log('Quiz data generated successfully:', {
      title: quizData.title,
      questionCount: quizData.questions?.length
    });

    // Try to fix any issues with the generated data
    console.log('Attempting to fix quiz data if needed...');
    try {
      quizData = fixQuizData(quizData);
      console.log('Quiz data fixed successfully');
    } catch (fixError) {
      console.error('Failed to fix quiz data:', fixError);
      // Continue with original data if fix fails
    }

    if (!quizData || !quizData.title || !Array.isArray(quizData.questions)) {
      throw new Error('Invalid quiz data structure after generation');
    }

    console.log('Creating quiz in database...');
    const quizId = await createQuiz(quizData.title, quizData.questions, quizData.keywords || []);
    console.log('Quiz saved successfully:', {
      id: quizId,
      title: quizData.title,
      questionCount: quizData.questions.length
    });
    
    res.status(201).json({ id: quizId });
  } catch (error) {
    console.error('Error generating quiz from file:', {
      error: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    });
    res.status(500).json({ 
      error: 'Failed to generate quiz from file',
      details: error.message 
    });
  }
});

export default router;
