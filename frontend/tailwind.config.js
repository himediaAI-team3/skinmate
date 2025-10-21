import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",        // ✅ 루트 app 폴더
    "./components/**/*.{js,ts,jsx,tsx,mdx}", // (있다면)
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",      // (있다면)
    "./features/**/*.{js,ts,jsx,tsx,mdx}",   // (있다면)
    // 필요하면 src 경로도 함께 유지
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-pretendard)'],
        gmarket: ['var(--font-gmarket)'],
      },
      colors: {
        brand: { orange: '#F97316', pink: '#EC4899' },
      },
    },
  },
  plugins: [],
};
export default config;

