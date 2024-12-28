# MCQ Quiz App

A multiple choice quiz application that supports both uploaded quizzes and quizzes from a directory.

## Adding New Quizzes

There are two ways to add quizzes to the application:

1. **Upload Quiz Files**: Use the upload button in the app to add quiz files. These can be modified or deleted through the app interface.

2. **Questions Directory**: Place JSON quiz files in the `public/questions` directory. These will be automatically loaded when the app starts. Files in this directory:
   - Are automatically available to all users
   - Cannot be deleted through the app interface
   - Will be loaded alongside any user-uploaded quizzes
   - Follow the same format as uploaded quizzes

### Quiz File Format

Quiz files should be JSON files with the following structure:

```json
{
    "title": "Quiz Title",
    "questions": [
        {
            "question": "Question text?",
            "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
            "correctAnswer": 1
        }
    ]
}
```

- `title`: The name of the quiz
- `questions`: Array of question objects
  - `question`: The question text
  - `options`: Array of possible answers
  - `correctAnswer`: Index of the correct answer (0-based)

### Example

See `public/questions/general-knowledge.json` for an example quiz file.
