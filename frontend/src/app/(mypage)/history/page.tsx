'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { Calendar, Trash2, Filter } from 'lucide-react';
import { MOCK_HISTORY } from '@/lib/mypage.mock';

// 카테고리 후보 (UI에 노출될 옵션)
const CATEGORY_OPTIONS = ['전체', '건선', '아토피', '여드름', '지루', '주사', '정상'] as const;
type CategoryOpt = typeof CATEGORY_OPTIONS[number];

const DATE_OPTIONS = ['전체', '1일전', '7일전', '한달전'] as const;
type DateOpt = typeof DATE_OPTIONS[number];

// summary 기반 간단 카테고리 추론 (데이터 변경 없이 필터용)
function inferCategory(summary: string): CategoryOpt {
  const s = summary.toLowerCase();
  if (s.includes('민감')) return '민감';
  if (s.includes('지성')) return '지성';
  if (s.includes('건성')) return '건성';
  if (s.includes('복합')) return '복합성';
  if (s.includes('중성')) return '중성';
  return '기타';
}

// "1일전/7일전/한달전" → 기준 일수
function daysFor(opt: DateOpt): number | null {
  switch (opt) {
    case '1일전':
      return 1;
    case '7일전':
      return 7;
    case '한달전':
      return 30;
    default:
      return null; // 전체
  }
}

type HistoryItem = (typeof MOCK_HISTORY)[number];

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>(MOCK_HISTORY);
  const [catFilter, setCatFilter] = useState<CategoryOpt>('전체');
  const [dateFilter, setDateFilter] = useState<DateOpt>('전체');

  const onDelete = (e: React.MouseEvent, id: number) => {
    e.preventDefault();   // 링크 이동 방지
    e.stopPropagation();  // 부모(Link) 클릭 이벤트 방지
    setItems((prev) => prev.filter((h) => h.id !== id));
  };

  // 필터링
  const filtered = useMemo(() => {
    const now = new Date();
    const d = daysFor(dateFilter);
    const cutoff = d ? new Date(now.getFullYear(), now.getMonth(), now.getDate() - d) : null;

    return items.filter((h) => {
      // 카테고리 필터
      const cat = inferCategory(h.summary);
      const passCat = catFilter === '전체' ? true : cat === catFilter;

      // 날짜 필터 (h.date: 'YYYY-MM-DD')
      const passDate =
        !cutoff
          ? true
          : new Date(h.date) >= cutoff; // 지정일수 이내만 표시

      return passCat && passDate;
    });
  }, [items, catFilter, dateFilter]);

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">분석 이력</h2>
      <p className="text-xs text-gray-500 mt-0.5">최근 진단명과 날짜만 간단히 보여드립니다.</p>

      {/* 상단 필터 바 */}
      <div className="mt-3 flex gap-2">
        {/* 카테고리 필터 */}
        <div className="relative flex-1">
          <select
            value={catFilter}
            onChange={(e) => setCatFilter(e.target.value as CategoryOpt)}
            aria-label="카테고리 필터"
            className="
              w-full appearance-none rounded-xl border border-gray-200 bg-white
              py-2.5 pl-3 pr-9 text-sm
              focus:border-orange-300 focus:ring-2 focus:ring-orange-200
            "
          >
            {CATEGORY_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          <Filter size={16} className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400" />
        </div>

        {/* 일자 필터 */}
        <div className="relative">
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value as DateOpt)}
            aria-label="일자 필터"
            className="
              appearance-none rounded-xl border border-gray-200 bg-white
              py-2.5 pl-3 pr-9 text-sm
              focus:border-orange-300 focus:ring-2 focus:ring-orange-200
            "
          >
            {DATE_OPTIONS.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
          <Filter size={16} className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400" />
        </div>
      </div>

      {/* 리스트 */}
      <div className="mt-3 divide-y divide-gray-100 rounded-2xl border border-gray-100 bg-white overflow-hidden">
        {filtered.map((h) => (
          <Link
            key={h.id}
            href={`/result/${h.id}`}
            className="flex items-center gap-3 p-4 hover:bg-gray-50 transition relative"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">{h.summary}</p>
              <p className="mt-0.5 inline-flex items-center gap-1 text-xs text-gray-500">
                <Calendar size={14} />
                <span>{h.date}</span>
              </p>
            </div>

            {/* 우측: 휴지통 버튼 (화살표 제거, 같은 자리 대체) */}
            <button
              type="button"
              aria-label="이 진단 이력 삭제"
              title="삭제"
              onClick={(e) => onDelete(e, h.id)}
              className="
                h-9 w-9 inline-flex items-center justify-center rounded-full
                border border-white/60 bg-white/80 backdrop-blur
                text-gray-700 hover:text-red-600 hover:border-red-200 hover:bg-red-50
                shadow-sm transition
              "
            >
              <Trash2 size={16} />
            </button>
          </Link>
        ))}

        {filtered.length === 0 && (
          <div className="p-4 text-sm text-gray-500 text-center">조건에 맞는 분석 이력이 없습니다.</div>
        )}
      </div>
    </section>
  );
}
