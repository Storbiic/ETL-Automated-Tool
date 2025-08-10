import type { Metadata } from "next";
import { ThemeProvider } from '@/contexts/ThemeContext';
import "./globals.css";

export const metadata: Metadata = {
  title: "ETL Automation Tool",
  description: "Modern React + Next.js ETL automation tool with custom theming",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased transition-colors duration-300">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
