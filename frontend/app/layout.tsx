import type { Metadata } from 'next';
import './globals.css';
import './siksha.css';

export const metadata: Metadata = {
  title: 'Siksha | Learning, connected to experience',
  description: 'A learning and internship platform by Tech & Trend Media Pvt. Ltd., Sanjay Palace, Agra.',
  icons: { icon: '/tech-trend-favicon.png', apple: '/tech-trend-favicon.png' },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><head><link rel="preconnect" href="https://fonts.googleapis.com"/><link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous"/></head><body>{children}</body></html>;
}
