'use client';

import { ETLDashboard } from '@/components/ETLDashboard';
import { ErrorBoundary } from '@/components/ErrorBoundary';

export default function Home() {
  return (
    <ErrorBoundary>
      <ETLDashboard />
    </ErrorBoundary>
  );
}
