import { useState } from 'react';
import { LocalStorageManager } from '../utils/LocalStorageManager';

export function QuizOptions({ preferences: initialPreferences, onPreferencesChange }) {
  const [preferences, setPreferences] = useState(initialPreferences);

  const handlePreferencesChange = (changes) => {
    const newPrefs = { ...preferences, ...changes };
    if (LocalStorageManager.saveQuizPreferences(newPrefs)) {
      setPreferences(newPrefs);
      onPreferencesChange(newPrefs);
    }
  };

  return (
    <div className="quiz-section">
      <h2 className="section-title">Options</h2>
      <div className="quiz-options">
        <div className="option-controls">
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.showTimer}
              onChange={(e) => handlePreferencesChange({ showTimer: e.target.checked })}
            />
            Show Timer
          </label>
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.showAnswersStraightaway}
              onChange={(e) => handlePreferencesChange({ showAnswersStraightaway: e.target.checked })}
            />
            Show choices straightaway
          </label>
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.hideAnswerFeedback}
              onChange={(e) => handlePreferencesChange({ hideAnswerFeedback: e.target.checked })}
            />
            Hide answer feedback until quiz finished
          </label>
          <label className="option-label">
            <input
              type="checkbox"
              checked={preferences.randomizeQuestions}
              onChange={(e) => handlePreferencesChange({ randomizeQuestions: e.target.checked })}
            />
            Randomize question order
          </label>
        </div>
      </div>
    </div>
  );
}
