export const sampleQuiz = {
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
