import type { Metadata } from 'next';
import { Poppins, JetBrains_Mono } from 'next/font/google';
import { AuthProvider } from '@/lib/auth';
import '@/styles/global.css';

const poppins = Poppins({
  subsets: ['latin', 'latin-ext'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-poppins',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'MyoLab-AI — sEMG Clinical Intelligence Platform',
  description:
    'Nền tảng Clinical Intelligence phân tích tín hiệu điện cơ bề mặt sEMG, phục vụ phục hồi chức năng sau đột quỵ và đánh giá vận động chi trên. Prototype với dữ liệu mô phỏng.',
  robots: 'noindex, nofollow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={`${poppins.variable} ${jetbrainsMono.variable}`}>
      <body>
          <AuthProvider>{children}</AuthProvider>
        </body>
    </html>
  );
}
