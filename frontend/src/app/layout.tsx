import type { Metadata } from "next";
import { Inter } from "next/font/google";
// @ts-ignore: side-effect import of global CSS
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FermentAI — Data Lake de Fermentación de Café",
  description: "Plataforma científica para gestión de datasets de imágenes de fermentación correlacionadas con datos HPLC",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
