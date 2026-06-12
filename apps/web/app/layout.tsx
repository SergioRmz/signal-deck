import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'signal-deck / Next.js renderer',
  description: 'Component-driven executive briefing renderer for signal-deck.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
