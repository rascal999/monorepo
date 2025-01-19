-- Insert a sample quiz
INSERT INTO quizzes (title) VALUES ('JavaScript Fundamentals') RETURNING id;

-- Insert questions and answers for the quiz (using the ID from above)
WITH quiz AS (
  SELECT id FROM quizzes WHERE title = 'JavaScript Fundamentals'
)
INSERT INTO questions (quiz_id, question_text, explanation)
VALUES 
  ((SELECT id FROM quiz), 'What is the output of typeof null?', 'While null is a primitive value in JavaScript, typeof null returns "object". This is a known quirk in JavaScript that has persisted for historical reasons.'),
  ((SELECT id FROM quiz), 'What is closure in JavaScript?', 'A closure is a function that has access to variables in its outer (enclosing) lexical scope, even after the outer function has returned.'),
  ((SELECT id FROM quiz), 'What is the difference between == and === in JavaScript?', 'The == operator performs type coercion before comparison, while === compares both value and type without coercion.');

-- Insert answers for the first question
WITH q AS (
  SELECT id FROM questions 
  WHERE question_text = 'What is the output of typeof null?'
)
INSERT INTO answers (question_id, answer_text, is_correct)
VALUES
  ((SELECT id FROM q), '"object"', true),
  ((SELECT id FROM q), '"null"', false),
  ((SELECT id FROM q), '"undefined"', false),
  ((SELECT id FROM q), 'null', false);

-- Insert answers for the second question
WITH q AS (
  SELECT id FROM questions 
  WHERE question_text = 'What is closure in JavaScript?'
)
INSERT INTO answers (question_id, answer_text, is_correct)
VALUES
  ((SELECT id FROM q), 'A function that has access to variables in its outer scope', true),
  ((SELECT id FROM q), 'A way to close a function', false),
  ((SELECT id FROM q), 'A method to end a loop', false),
  ((SELECT id FROM q), 'A type of JavaScript object', false);

-- Insert answers for the third question
WITH q AS (
  SELECT id FROM questions 
  WHERE question_text = 'What is the difference between == and === in JavaScript?'
)
INSERT INTO answers (question_id, answer_text, is_correct)
VALUES
  ((SELECT id FROM q), '== compares values with type coercion, === compares values and types', true),
  ((SELECT id FROM q), 'They are exactly the same', false),
  ((SELECT id FROM q), '=== is just a syntax error', false),
  ((SELECT id FROM q), '== is used for numbers, === is used for strings', false);
