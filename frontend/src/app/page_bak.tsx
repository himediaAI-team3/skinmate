// app/page.tsx
'use client';

import Link from 'next/link';

export default function MainPage() {
  const recentDate = '10월 22일';
  const recentSummary = '지복합성, 민감성';

  const recommended = [
    { id: 1, title: '수딩 시카 크림', sub: '민감 피부용', img: 'https://placehold.co/640x640/FFE0B2/FF6B6B?text=Product+1', href: '/product/1' },
    { id: 2, title: '오일프리 선스크린', sub: '지성 피부용', img: 'https://placehold.co/640x640/B2DFDB/00796B?text=Product+2', href: '/product/2' },
    { id: 3, title: '히알루론산 토너', sub: '모든 피부용', img: 'https://placehold.co/640x640/E1BEE7/6A1B9A?text=Product+3', href: '/product/3' },
  ];

  return (
    <main className="px-5 pt-4">
      {/* 1) 헤더 섹션 */}
      <section className="space-y-1">
        <h2 className="text-[22px] font-extrabold tracking-tight text-gray-900">
          <span className="bg-gradient-to-r from-orange-500 to-pink-500 bg-clip-text text-transparent">
            오늘의 스킨 인사이트
          </span>
        </h2>
        <p className="text-gray-500 text-sm">오늘의 피부 상태에 맞는 솔루션을 확인해보세요.</p>
      </section>

      {/* 2) 최근 진단 */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-gray-900">나의 최근 피부 진단</h3>
          <span className="inline-flex items-center gap-1 rounded-full bg-gray-100 px-2.5 py-1 text-[11px] font-medium text-gray-600 ring-1 ring-gray-200">
            {recentDate}
          </span>
        </div>

        <div className="relative overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
          {/* 은은한 라이트 */}
          <div className="pointer-events-none absolute -top-16 right-0 h-40 w-40 rounded-full bg-gradient-to-br from-orange-200/40 to-pink-200/40 blur-2xl" />
          <div className="relative grid gap-3 p-4">
            <div className="rounded-xl bg-gradient-to-br from-gray-50 to-white p-4 ring-1 ring-gray-100/80 backdrop-blur">
              <p className="text-xs text-gray-500">AI 분석 결과</p>
              <p className="mt-1 text-xl font-extrabold tracking-tight text-gray-900">{recentSummary}</p>
            </div>
            <div className="flex items-center justify-between">
              <p className="text-[11px] text-gray-400">최신 분석을 기준으로 추천이 업데이트됩니다.</p>
              <Link
                href="/result/123"
                className="inline-flex items-center rounded-full bg-gradient-to-r from-orange-500 to-pink-500 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:opacity-95"
              >
                자세히 보기
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 3) 추천 리스트 */}
      <section className="space-y-4">
        <div className="flex items-baseline justify-between">
          <div>
            <h3 className="text-lg font-bold text-gray-900">AI 맞춤 추천 제품</h3>
            <p className="mt-0.5 text-xs text-gray-500">내 피부 타입에 꼭 맞는 제품만 모았어요.</p>
          </div>
          <Link href="/recommend" className="text-xs font-medium text-gray-500 hover:text-gray-700">
            전체보기
          </Link>
        </div>

        <div className="flex gap-4 overflow-x-auto pb-2">
          {recommended.map((p) => (
            <article key={p.id} className="w-40 flex-shrink-0">
              <Link
                href={p.href}
                className="group block overflow-hidden rounded-xl border border-gray-100 bg-white shadow-sm transition hover:shadow-md"
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <div className="relative aspect-square w-full">
                  <img src={p.img} alt={p.title} className="h-full w-full object-cover" />
                  {/* 이미지 오버레이 그라데이션 */}
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/20 via-black/0 to-transparent opacity-0 transition group-hover:opacity-100" />
                </div>
                <div className="p-3">
                  <h4 className="truncate text-sm font-semibold text-gray-900">{p.title}</h4>
                  <p className="mt-0.5 text-[11px] text-gray-500">{p.sub}</p>
                </div>
              </Link>
            </article>
          ))}
        </div>
      </section>

      {/* 4) CTA */}
      <section className="space-y-3">
        <div className="rounded-2xl bg-gradient-to-r from-orange-50 to-pink-50 p-4 ring-1 ring-orange-100/60">
          <Link
            href="/info"
            className="relative block w-full rounded-2xl bg-gradient-to-r from-orange-500 to-pink-500 py-4 px-6 text-center text-[15px] font-bold text-white shadow-md transition hover:shadow-lg"
          >
            {/* 글로우 */}
            <span className="pointer-events-none absolute inset-0 -z-10 rounded-2xl bg-gradient-to-r from-orange-500/30 to-pink-500/30 blur-xl" />
            AI 피부 진단 다시하기
          </Link>
        </div>
        <p className="text-center text-[11px] text-gray-400">* 정확한 분석을 위해 조명과 초점을 확인해 주세요.</p>
      </section>

      {/* 5) 보조 컨텐츠 */}
      <section className="space-y-3">
        <h3 className="text-lg font-bold text-gray-900">도움이 될만한 것들</h3>
        <div className="grid grid-cols-2 gap-3">
          <Link
            href="/tips"
            className="group rounded-xl border border-gray-100 bg-white p-4 shadow-sm ring-1 ring-transparent transition hover:shadow-md hover:ring-gray-200"
          >
            <p className="text-[13px] font-semibold text-gray-900">오늘의 케어 팁</p>
            <p className="mt-1 line-clamp-2 text-[12px] text-gray-500">
              세안 후 3분 내 보습제를 바르면 수분 손실을 줄일 수 있어요.
            </p>
            <span className="mt-2 inline-block text-[11px] font-medium text-gray-400">더 알아보기 →</span>
          </Link>
          <Link
            href="/routines"
            className="group rounded-xl border border-gray-100 bg-white p-4 shadow-sm ring-1 ring-transparent transition hover:shadow-md hover:ring-gray-200"
          >
            <p className="text-[13px] font-semibold text-gray-900">루틴 가이드</p>
            <p className="mt-1 line-clamp-2 text-[12px] text-gray-500">
              아침/저녁 루틴을 저장하고 리마인더로 꾸준히 관리해 보세요.
            </p>
            <span className="mt-2 inline-block text-[11px] font-medium text-gray-400">시작하기 →</span>
          </Link>
        </div>
      </section>

      {/* 6) 푸터 노트 */}
      <footer className="pt-2">
        <p className="text-center text-[11px] text-gray-400">• 피부 개선은 개인차가 있습니다 •</p>
      </footer>
    </main>
  );
}
