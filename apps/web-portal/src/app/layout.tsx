import type { Metadata } from 'next';
import { AuthProvider } from '@/lib/auth';
import '@/styles/global.css';

export const metadata: Metadata = {
  title: 'MyoLab-AI — sEMG Quality Intelligence Research Portal',
  description:
    'Cổng nghiên cứu phân tích chất lượng tín hiệu điện cơ bề mặt sEMG. Research-only prototype với dữ liệu mô phỏng, không dùng cho mục đích lâm sàng.',
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
