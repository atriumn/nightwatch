import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
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
  title: "Noxaudit - AI-Powered Codebase Audits",
  description:
    "Nightly AI-powered codebase audits with rotating focus areas, multi-provider support, and decision memory. Find real issues, not noise.",
  openGraph: {
    title: "Noxaudit - AI-Powered Codebase Audits",
    description:
      "Nightly AI-powered codebase audits with rotating focus areas. Find real issues, not noise.",
    url: "https://noxaudit.com",
    siteName: "Noxaudit",
    type: "website",
    images: [
      {
        url: "https://noxaudit.com/lighthouse-near.png",
        width: 1200,
        height: 630,
        alt: "Noxaudit - AI-powered codebase audits",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Noxaudit - AI-Powered Codebase Audits",
    description:
      "Nightly AI-powered codebase audits with rotating focus areas. Find real issues, not noise.",
    images: ["https://noxaudit.com/lighthouse-near.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans antialiased`}
      >
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
