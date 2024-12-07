# MCQ Quiz Application

A modern, interactive Multiple Choice Question (MCQ) quiz application built with React and Vite.

## Features

- Dynamic question navigation with pagination
- Question flagging for later review
- Timer tracking for each question
- Answer hiding/revealing functionality
- Dark/Light theme support
- Progress tracking
- Results summary with detailed statistics
- Question-by-question review
- Support for uploading custom quiz files

## Getting Started

### Prerequisites

- Node.js (v14 or higher)
- npm (v6 or higher)

### Installation

1. Clone the repository
2. Install dependencies:
```bash
npm install
```

### Development

Run the development server:
```bash
npm run dev
```

### Building for Production

Build the application:
```bash
npm run build
```

## Usage

### Taking a Quiz

1. Upload a quiz file in the supported JSON format
2. Navigate through questions using:
   - Next/Previous buttons
   - Question number buttons
   - Pagination controls
3. Flag questions for later review using the flag icon
4. Toggle answer visibility as needed
5. Submit answers and view detailed results

### Question Flagging

- Click the flag icon below any question number to mark it for review
- Click again to unflag
- Flagged questions are visually marked for easy identification
- Use flags to track questions you want to revisit later

### Quiz File Format

```json
{
  "title": "Quiz Title",
  "questions": [
    {
      "question": "Question text",
      "options": [
        "Option 1",
        "Option 2",
        "Option 3",
        "Option 4"
      ],
      "correctAnswer": 0
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.
