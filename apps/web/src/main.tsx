import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import App from './App';
import { Shell } from './layout';

const root = document.getElementById('root');

if (!root) {
  throw new Error('Root element #root was not found.');
}

createRoot(root).render(
  <StrictMode>
    <Shell>
      <App />
    </Shell>
  </StrictMode>,
);
