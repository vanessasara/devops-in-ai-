/**
 * Quiz Component
 * Interactive Textbook - Agentic AI in DevOps
 *
 * Displays chapter quizzes with multiple-choice questions.
 * Supports quiz submission and shows results with explanations.
 */

import React, { useState, useEffect } from 'react';

/**
 * Quiz Component Props
 * @param {string} chapterSlug - The chapter identifier
 * @param {function} onComplete - Callback when quiz is completed (optional)
 */
export default function QuizComponent({ chapterSlug, onComplete }) {
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState({});
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const apiBaseUrl = typeof window !== 'undefined'
    ? (window.__BACKEND_URL__ || 'http://localhost:8000')
    : 'http://localhost:8000';

  // Check authentication status
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/auth/session`, {
          credentials: 'include',
        });
        setIsAuthenticated(response.ok);
      } catch {
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, [apiBaseUrl]);

  // Fetch quiz
  useEffect(() => {
    const fetchQuiz = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(`${apiBaseUrl}/api/quiz/${chapterSlug}`, {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('Failed to load quiz');
        }

        const data = await response.json();
        setQuiz(data);

        // Initialize answers
        const initialAnswers = {};
        data.questions.forEach((q) => {
          initialAnswers[q.id] = null;
        });
        setAnswers(initialAnswers);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load quiz');
      } finally {
        setIsLoading(false);
      }
    };

    fetchQuiz();
  }, [chapterSlug, apiBaseUrl]);

  const handleAnswerSelect = (questionId, optionIndex) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionIndex,
    }));
  };

  const handleSubmit = async () => {
    if (!isAuthenticated) {
      setError('Please sign in to submit your quiz');
      return;
    }

    // Check all questions answered
    const unanswered = Object.values(answers).filter((a) => a === null);
    if (unanswered.length > 0) {
      setError('Please answer all questions before submitting');
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/quiz/${chapterSlug}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          answers: Object.entries(answers).map(([questionId, selectedIndex]) => ({
            questionId,
            selectedIndex,
          })),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit quiz');
      }

      const data = await response.json();
      setResult(data);

      if (onComplete) {
        onComplete(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit quiz');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetry = () => {
    setResult(null);
    const initialAnswers = {};
    quiz.questions.forEach((q) => {
      initialAnswers[q.id] = null;
    });
    setAnswers(initialAnswers);
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="quiz-container">
        <div className="quiz-loading">
          <span className="loading-spinner" />
          <span>Loading quiz...</span>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !quiz) {
    return (
      <div className="quiz-container">
        <div className="quiz-error">
          <p>⚠️ {error}</p>
          <button className="retry-button" onClick={() => window.location.reload()}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  // No quiz available
  if (!quiz) {
    return null;
  }

  // Result display
  if (result) {
    return (
      <div className="quiz-container">
        <div className="quiz-result">
          <h3>Quiz Results</h3>
          <div className="score-display">
            <span className="score-number">{result.score}</span>
            <span className="score-divider">/</span>
            <span className="score-total">{result.total}</span>
          </div>
          <p className="score-percentage">
            {Math.round((result.score / result.total) * 100)}% Correct
          </p>

          {quiz.reflectionPrompt && (
            <div className="reflection-prompt">
              <h4>Reflection</h4>
              <p>{quiz.reflectionPrompt}</p>
            </div>
          )}

          <div className="result-actions">
            <button className="retry-button" onClick={handleRetry}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Quiz display
  return (
    <div className="quiz-container">
      <div className="quiz-header">
        <h3>Chapter Quiz</h3>
        <p className="quiz-instruction">
          Test your understanding of this chapter. Answer all 4 questions.
        </p>
      </div>

      {!isAuthenticated && (
        <div className="quiz-auth-notice">
          <p>Sign in to save your quiz results and track your progress.</p>
          <a href="/login" className="auth-link">Sign In</a>
        </div>
      )}

      <div className="quiz-questions">
        {quiz.questions.map((question, qIndex) => (
          <div
            key={question.id}
            className={`quiz-question ${answers[question.id] !== null ? 'answered' : ''}`}
          >
            <p className="question-number">Question {qIndex + 1}</p>
            <p className="question-text">{question.question}</p>

            <div className="question-options">
              {question.options.map((option, oIndex) => (
                <label
                  key={oIndex}
                  className={`option-label ${
                    answers[question.id] === oIndex ? 'selected' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name={`question-${question.id}`}
                    value={oIndex}
                    checked={answers[question.id] === oIndex}
                    onChange={() => handleAnswerSelect(question.id, oIndex)}
                  />
                  <span className="option-text">{option}</span>
                </label>
              ))}
            </div>
          </div>
        ))}
      </div>

      {error && (
        <div className="quiz-error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="quiz-actions">
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={isSubmitting || Object.values(answers).some((a) => a === null)}
        >
          {isSubmitting ? (
            <>
              <span className="loading-spinner-small" />
              Submitting...
            </>
          ) : (
            'Submit Answers'
          )}
        </button>
      </div>

      {quiz.reflectionPrompt && !result && (
        <div className="reflection-hint">
          <p>After completing the quiz, reflect on: {quiz.reflectionPrompt}</p>
        </div>
      )}
    </div>
  );
}