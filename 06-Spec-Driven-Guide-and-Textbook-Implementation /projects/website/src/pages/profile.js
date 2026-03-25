/**
 * Profile Settings Page
 * User profile management for background preference and quiz history
 */

import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { Redirect } from '@docusaurus/router';

interface UserProfile {
  id: string;
  email: string;
  background: string;
}

interface QuizResult {
  chapterSlug: string;
  score: number;
  completedAt: string;
}

const BACKGROUND_OPTIONS = [
  { value: 'beginner', label: 'Beginner - New to AI/DevOps', description: 'Content focuses on fundamentals and concepts' },
  { value: 'engineer', label: 'Engineer - Some technical experience', description: 'Balanced technical depth with practical examples' },
  { value: 'architect', label: 'Architect - Designs systems', description: 'Advanced patterns and architectural considerations' },
  { value: 'manager', label: 'Manager - Leads teams', description: 'Focus on leadership and strategic implications' },
];

const CHAPTER_NAMES: Record<string, string> = {
  'intro': 'Introduction to Agentic AI',
  'core-building-blocks': 'Core Building Blocks',
  'patterns': 'Agent Patterns',
  'tools': 'Tool Use & Integration',
  'observability': 'Observability & Monitoring',
  'security': 'Security Considerations',
  'scaling': 'Scaling Patterns',
};

export default function ProfilePage() {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [quizResults, setQuizResults] = useState<QuizResult[]>([]);
  const [selectedBackground, setSelectedBackground] = useState<string>('engineer');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

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

        if (response.ok) {
          const data = await response.json();
          setUser(data.user);
          setSelectedBackground(data.user.background);
          setIsAuthenticated(true);
        } else {
          setIsAuthenticated(false);
        }
      } catch {
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [apiBaseUrl]);

  // Fetch quiz results when authenticated
  useEffect(() => {
    if (!user) return;

    const fetchQuizResults = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/quiz/results`, {
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setQuizResults(data);
        }
      } catch (err) {
        console.error('Failed to fetch quiz results:', err);
      }
    };

    fetchQuizResults();
  }, [user, apiBaseUrl]);

  const handleBackgroundChange = async (newBackground: string) => {
    if (!user || newBackground === user.background) return;

    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${apiBaseUrl}/api/user/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ background: newBackground }),
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const updatedUser = await response.json();
      setUser(updatedUser);
      setSelectedBackground(newBackground);
      setSuccess('Profile updated successfully!');

      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch(`${apiBaseUrl}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include',
      });
      window.location.href = '/';
    } catch (err) {
      console.error('Logout failed:', err);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Layout title="Profile">
        <div className="profile-container">
          <div className="profile-loading">
            <span className="loading-spinner" />
            <span>Loading profile...</span>
          </div>
        </div>
      </Layout>
    );
  }

  // Not authenticated - redirect to login
  if (isAuthenticated === false) {
    return (
      <Layout title="Profile">
        <div className="profile-container">
          <div className="profile-auth-required">
            <h2>Authentication Required</h2>
            <p>Please sign in to view your profile and personalize your learning experience.</p>
            <a href="/login" className="auth-link">Sign In</a>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title="Profile">
      <div className="profile-container">
        <div className="profile-card">
          {/* Header */}
          <div className="profile-header">
            <h1>Your Profile</h1>
            <p className="profile-email">{user?.email}</p>
          </div>

          {/* Messages */}
          {error && (
            <div className="profile-error">
              ⚠️ {error}
            </div>
          )}
          {success && (
            <div className="profile-success">
              ✓ {success}
            </div>
          )}

          {/* Background Preference */}
          <section className="profile-section">
            <h2>Background Preference</h2>
            <p className="section-description">
              Select your background to personalize content recommendations and explanations.
            </p>

            <div className="background-options">
              {BACKGROUND_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className={`background-option ${selectedBackground === option.value ? 'selected' : ''}`}
                >
                  <input
                    type="radio"
                    name="background"
                    value={option.value}
                    checked={selectedBackground === option.value}
                    onChange={() => setSelectedBackground(option.value)}
                    disabled={isSaving}
                  />
                  <div className="option-content">
                    <span className="option-label">{option.label}</span>
                    <span className="option-description">{option.description}</span>
                  </div>
                </label>
              ))}
            </div>

            <button
              className="save-button"
              onClick={() => handleBackgroundChange(selectedBackground)}
              disabled={isSaving || selectedBackground === user?.background}
            >
              {isSaving ? (
                <>
                  <span className="loading-spinner-small" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </section>

          {/* Quiz Results */}
          <section className="profile-section">
            <h2>Quiz Results</h2>
            <p className="section-description">
              Your quiz completion history across chapters.
            </p>

            {quizResults.length === 0 ? (
              <div className="empty-state">
                <p>No quiz results yet.</p>
                <p>Complete chapter quizzes to track your progress here.</p>
              </div>
            ) : (
              <div className="quiz-results-list">
                {quizResults.map((result, index) => (
                  <div key={index} className="quiz-result-item">
                    <div className="result-info">
                      <span className="chapter-name">
                        {CHAPTER_NAMES[result.chapterSlug] || result.chapterSlug}
                      </span>
                      <span className="result-date">
                        {new Date(result.completedAt).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="result-score">
                      <span className="score-value">{result.score}</span>
                      <span className="score-total">/4</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Account Actions */}
          <section className="profile-section">
            <h2>Account</h2>
            <button className="logout-button" onClick={handleLogout}>
              Sign Out
            </button>
          </section>
        </div>
      </div>
    </Layout>
  );
}