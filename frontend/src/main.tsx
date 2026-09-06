import React from 'react';
import project from '@/app/project.json';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from '@tanstack/react-router';

import { enableMocking } from '@/shared/api/enableMocking';
import { router } from '@/app/router';
import '@/shared/styles/global.css';

async function bootstrap() {
  document.title = project.name;
  await enableMocking();

  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error(
      'Unable to initialize CFO Command Center: root element is missing.',
    );
  }

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <RouterProvider router={router} />
    </React.StrictMode>,
  );
}

void bootstrap();
