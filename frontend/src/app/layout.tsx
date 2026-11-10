import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL || "http://localhost:3000"
  ),
  title: {
    default: "ShellFinance | Your Money. Your Future. Your Control.",
    template: "%s | ShellFinance",
  },
  description:
    "An intelligent personal finance platform designed to bring financial clarity, investment insights and better money management together.",
  applicationName: "ShellFinance",
  keywords: [
    "ShellFinance",
    "personal finance",
    "money management",
    "financial planning",
    "investment insights",
  ],
  openGraph: {
    title: "ShellFinance",
    description:
      "Take control of your financial life with intelligent money management and financial insights.",
    siteName: "ShellFinance",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">{children}</body>
    </html>
  );
}
