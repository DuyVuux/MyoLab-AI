import type { Metadata } from 'next';
import { AuthProvider } from '@/lib/auth';
import '@/styles/global.css';

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
    <html lang="vi">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
