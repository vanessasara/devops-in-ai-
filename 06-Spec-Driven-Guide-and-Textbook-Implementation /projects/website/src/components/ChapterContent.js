/**
 * Chapter Content Wrapper
 * Interactive Textbook - Agentic AI in DevOps
 *
 * Wraps MDX content with interactive elements like summaries and quizzes.
 */

import React from 'react';
import ChapterSummary from './ChapterSummary';
import QuizComponent from './QuizComponent';

/**
 * Chapter Content Props
 * @param {string} slug - The chapter identifier
 * @param {React.ReactNode} children - The MDX content
 */
export default function ChapterContent({ slug, children }) {
  return (
    <div className="interactive-chapter">
      {/* Top Summary Section */}
      <ChapterSummary slug={slug} />

      {/* Main Chapter Content */}
      <div className="chapter-body">
        {children}
      </div>

      {/* Bottom Quiz Section */}
      <div className="chapter-footer">
        <hr className="footer-divider" />
        <QuizComponent chapterSlug={slug} />
      </div>
    </div>
  );
}
