/**
 * Chapter Summary Component
 * Interactive Textbook - Agentic AI in DevOps
 *
 * Displays a 3-5 bullet point summary of the chapter.
 * Fetches personalized summaries based on user background.
 */

import React, { useState, useEffect } from 'react';

/**
 * Chapter Summary Component Props
 * @param {string} slug - The chapter identifier
 */
export default function ChapterSummary({ slug }) {
  const [summaryData, setSummaryData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [background, setBackground] = useState('engineer');

  const apiBaseUrl = typeof window !== 'undefined'
    ? (window.__BACKEND_URL__ || 'http://localhost:8000')
    : 'http://localhost:8000';

  // Load user background from session/profile
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/user/profile`, {
          credentials: 'include',
        });
        if (response.ok) {
          const profile = await response.json();
          setBackground(profile.background || 'engineer');
        }
      } catch (err) {
        console.error('Failed to fetch profile for background personalization:', err);
      }
    };
    fetchProfile();
  }, [apiBaseUrl]);

  // Fetch summary when slug or background changes
  useEffect(() => {
    const fetchSummary = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const url = new URL(`${apiBaseUrl}/api/chapters/${slug}/summary`);
        url.searchParams.append('background', background);

        const response = await fetch(url.toString(), {
          credentials: 'include',
        });

        if (!response.ok) {
          throw new Error('Failed to load chapter summary');
        }

        const data = await response.json();
        setSummaryData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load summary');
      } finally {
        setIsLoading(false);
      }
    };

    if (slug) {
      fetchSummary();
    }
  }, [slug, background, apiBaseUrl]);

  if (isLoading) {
    return (
      <div className="chapter-summary-loading">
        <span className="loading-spinner-small" />
        <span>Generating summary...</span>
      </div>
    );
  }

  if (error || !summaryData) {
    return (
      <div className="chapter-summary-error">
        <p>⚠️ Could not load summary. Please check the chapter content below.</p>
      </div>
    );
  }

  return (
    <div className="chapter-summary-container">
      <div className="chapter-summary-header">
        <div className="summary-badge">
          {background.charAt(0).toUpperCase() + background.slice(1)} Perspective
        </div>
        <h3 className="summary-title">Key Takeaways</h3>
      </div>
      
      <ul className="summary-bullets">
        {summaryData.summary.map((bullet, index) => (
          <li key={index} className="summary-bullet">
            {bullet}
          </li>
        ))}
      </ul>

      {summaryData.keyTerms && summaryData.keyTerms.length > 0 && (
        <div className="key-terms-section">
          <h4 className="key-terms-title">Key Terms</h4>
          <div className="key-terms-list">
            {summaryData.keyTerms.map((item, index) => (
              <div key={index} className="key-term-item">
                <span className="key-term-name">{item.term}:</span>
                <span className="key-term-definition">{item.definition}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
