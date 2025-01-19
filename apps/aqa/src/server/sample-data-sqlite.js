import { initDb } from './db.js';

async function loadSampleData() {
  const db = await initDb();
  
  try {
    // Start transaction
    await db.run('BEGIN TRANSACTION');
    
    // Insert quiz
    const quizResult = await db.run(
      'INSERT INTO quizzes (title) VALUES (?)',
      ['JavaScript Fundamentals']
    );
    const quizId = quizResult.lastID;
    
    // Insert questions
    const questions = [
      {
        text: 'What is the output of typeof null?',
        explanation: 'While null is a primitive value in JavaScript, typeof null returns "object". This is a known quirk in JavaScript that has persisted for historical reasons.',
        answers: [
          { text: '"object"', correct: true },
          { text: '"null"', correct: false },
          { text: '"undefined"', correct: false },
          { text: 'null', correct: false }
        ]
      },
      {
        text: 'What is closure in JavaScript?',
        explanation: 'A closure is a function that has access to variables in its outer (enclosing) lexical scope, even after the outer function has returned.',
        answers: [
          { text: 'A function that has access to variables in its outer scope', correct: true },
          { text: 'A way to close a function', correct: false },
          { text: 'A method to end a loop', correct: false },
          { text: 'A type of JavaScript object', correct: false }
        ]
      },
      {
        text: 'What is the difference between == and === in JavaScript?',
        explanation: 'The == operator performs type coercion before comparison, while === compares both value and type without coercion.',
        answers: [
          { text: '== compares values with type coercion, === compares values and types', correct: true },
          { text: 'They are exactly the same', correct: false },
          { text: '=== is just a syntax error', correct: false },
          { text: '== is used for numbers, === is used for strings', correct: false }
        ]
      }
    ];
    
    for (const q of questions) {
      const questionResult = await db.run(
        'INSERT INTO questions (quiz_id, question_text, explanation) VALUES (?, ?, ?)',
        [quizId, q.text, q.explanation]
      );
      const questionId = questionResult.lastID;
      
      for (const a of q.answers) {
        await db.run(
          'INSERT INTO answers (question_id, answer_text, is_correct) VALUES (?, ?, ?)',
          [questionId, a.text, a.correct ? 1 : 0]
        );
      }
    }
    
    await db.run('COMMIT');
    console.log('Sample data loaded successfully!');
  } catch (error) {
    await db.run('ROLLBACK');
    console.error('Error loading sample data:', error);
    throw error;
  }
}

loadSampleData().catch(console.error);
