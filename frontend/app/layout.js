import "./globals.css";
import { Baloo_2, Nunito } from "next/font/google";
import { LanguageProvider } from "./lib/LanguageContext";

// next/font self-hosts these at build time (no external font-CDN request at runtime,
// unlike the ouder-dashboard mockup's base64 data-URI trick - that was only needed
// because the Artifact sandbox blocks font CDNs; a real Next.js app doesn't have that
// restriction). Exposed as CSS variables the @theme block in globals.css maps to
// font-display/font-body.
const baloo2 = Baloo_2({ subsets: ["latin"], weight: ["700"], variable: "--font-baloo2" });
const nunito = Nunito({ subsets: ["latin"], weight: ["400", "600", "700", "800"], variable: "--font-nunito" });

export const metadata = {
  title: "Math Tutor MVP",
  description: "AI adaptive math tutor — placeholder deployment",
};

export default function RootLayout({ children }) {
  // lang="nl" is the server-rendered default (matches this app's Dutch-first
  // audience) - LanguageContext syncs it client-side once a stored preference loads.
  return (
    <html lang="nl" className={`${baloo2.variable} ${nunito.variable}`}>
      <body className="font-body">
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
