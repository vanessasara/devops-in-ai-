/**
 * Previous/Next Navigation Component
 * Displays navigation between chapters with titles and progress
 */

import React from 'react';
import Link from '@docusaurus/Link';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import { useSidebar } from '@docusaurus/plugin-content-docs/client';

interface NavItem {
  title: string;
  slug: string;
}

interface PrevNextProps {
  prev?: NavItem | null;
  next?: NavItem | null;
}

export default function PrevNext({ prev, next }: PrevNextProps) {
  const { metadata } = useDoc();
  const sidebar = useSidebar();

  // Get navigation items from sidebar if not provided
  const navItems = React.useMemo(() => {
    if (prev !== undefined || next !== undefined) {
      return { prev, next };
    }

    // Try to get from sidebar
    if (sidebar) {
      const currentIndex = sidebar.findIndex(
        (item: any) => item.docId === metadata.id
      );

      return {
        prev: currentIndex > 0 ? sidebar[currentIndex - 1] : null,
        next: currentIndex < sidebar.length - 1 ? sidebar[currentIndex + 1] : null,
      };
    }

    return { prev: null, next: null };
  }, [prev, next, sidebar, metadata.id]);

  return (
    <nav className="prev-next-nav" aria-label="Chapter navigation">
      <div className="prev-next-container">
        {navItems.prev && (
          <Link
            to={`/docs/${navItems.prev.slug || navItems.prev.id}`}
            className="prev-next-link prev-link"
            aria-label={`Previous: ${navItems.prev.title}`}
          >
            <span className="nav-direction">← Previous</span>
            <span className="nav-title">{navItems.prev.title}</span>
          </Link>
        )}

        {navItems.next && (
          <Link
            to={`/docs/${navItems.next.slug || navItems.next.id}`}
            className="prev-next-link next-link"
            aria-label={`Next: ${navItems.next.title}`}
          >
            <span className="nav-direction">Next →</span>
            <span className="nav-title">{navItems.next.title}</span>
          </Link>
        )}
      </div>
    </nav>
  );
}