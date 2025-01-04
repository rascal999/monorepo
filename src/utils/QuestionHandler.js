export class QuestionHandler {
  static validateQuestions(questions) {
    if (!Array.isArray(questions)) return false;
    
    return questions.every(q => 
      q.question && 
      Array.isArray(q.options) && 
      q.options.length >= 2 &&
      typeof q.correctAnswer === 'number' &&
      q.correctAnswer >= 0 &&
      q.correctAnswer < q.options.length
    );
  }

  static prepareQuestion(question) {
    // Create a copy of the options array with their original indices
    const optionsWithIndices = question.options.map((opt, index) => ({
      text: opt,
      originalIndex: index
    }));

    // Shuffle the options
    for (let i = optionsWithIndices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [optionsWithIndices[i], optionsWithIndices[j]] = [optionsWithIndices[j], optionsWithIndices[i]];
    }

    // Find the new index of the correct answer
    const newCorrectAnswerIndex = optionsWithIndices.findIndex(opt => 
      opt.originalIndex === question.correctAnswer
    );

    return {
      question: question.question,
      options: optionsWithIndices.map(opt => opt.text),
      correctAnswer: newCorrectAnswerIndex
    };
  }

  static prepareQuestions(questions, randomize = true) {
    let preparedQuestions = questions.map(q => this.prepareQuestion(q));
    
    if (randomize) {
      // Create array of indices and shuffle them
      const indices = Array.from({ length: preparedQuestions.length }, (_, i) => i);
      for (let i = indices.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [indices[i], indices[j]] = [indices[j], indices[i]];
      }
      
      // Reorder questions based on shuffled indices
      preparedQuestions = indices.map(i => preparedQuestions[i]);
    }
    
    return preparedQuestions;
  }

  static calculateScore(questions, userAnswers) {
    return userAnswers.reduce((score, answer, index) => {
      return score + (answer === questions[index].correctAnswer ? 1 : 0);
    }, 0);
  }

  static getQuestionSummary(questions, userAnswers) {
    return questions.map((q, index) => ({
      question: q.question,
      options: q.options,
      correctAnswer: q.correctAnswer,
      userAnswer: userAnswers[index]
    }));
  }
}
