// /src/app/history/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Calendar, Trash2, Filter } from 'lucide-react';
import { getAnalysisHistory, deleteAnalysis } from '@/features/history';
import type { AnalysisHistory } from '@/entities/history';

// 카테고리 후보 (UI에 노출될 옵션)
const CATEGORY_OPTIONS = ['전체', '건선', '아토피', '여드름', '지루', '주사', '정상'] as const;
type CategoryOpt = typeof CATEGORY_OPTIONS[number];

const DATE_OPTIONS = ['전체', '1일전', '7일전', '한달전'] as const;
type DateOpt = typeof DATE_OPTIONS[number];

// UI → API period 매핑
function mapPeriod(opt: DateOpt): 'all' | 'day' | 'week' | 'month' {
  switch (opt) {
    case '1일전':
      return 'day';
    case '7일전':
      return 'week';
    case '한달전':
      return 'month';
    default:
      return 'all';
  }
}
// UI → API disease_name 매핑
function mapDisease(opt: CategoryOpt): string {
  return opt === '전체' ? '' : opt;
}

// 날짜 표기 통합
function getDateStr(h: AnalysisHistory): string {
  const raw = (h as any).analyzed_at ?? (h as any).created_at ?? (h as any).date;
  if (!raw) return '';
  if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
  const d = new Date(raw);
  if (isNaN(d.getTime())) return String(raw);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

// UI 표시용: 서버 요약이 없을 때도 안전하게 표시
type Row = AnalysisHistory & { summary: string; member_id?: number };

export default function HistoryPage() {
  // 실제 로그인 유저 ID 사용 권장. 없으면 테스트용 .env 또는 1 사용
  const memberId =
    Number(process.env.NEXT_PUBLIC_TEST_MEMBER_ID ?? '') || 1;

  const [items, setItems] = useState<Row[]>([]);
  const [catFilter, setCatFilter] = useState<CategoryOpt>('전체');
  const [dateFilter, setDateFilter] = useState<DateOpt>('전체');
  const [loading, setLoading] = useState(false);

  // 서버 조회
  useEffect(() => {
    let alive = true;
    (async () => {
      setLoading(true);
      try {
        const res = await getAnalysisHistory({
          member_id: memberId,
          page: 1,
          size: 10,
          disease_name: mapDisease(catFilter),
          period: mapPeriod(dateFilter),
        });

        if (!alive) return;

        // 서버 → UI 정규화 (요약이 없으면 질환명으로 대체)
        const rows: Row[] = res.items.map((x: any) => ({
          id: x.id ?? x.analysis_id,
          member_id: x.member_id ?? memberId,
          disease_name: x.disease_name ?? x.diagnosis ?? '정상',
          analyzed_at: x.analyzed_at ?? x.created_at ?? x.date,
          summary:
            x.summary ??
            x.note ??
            x.title ??
            x.disease_name ??
            '분석 결과',
        }));
        setItems(rows);
      } catch {
        if (!alive) return;
        setItems([]);
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => {
      alive = false;
    };
  }, [memberId, catFilter, dateFilter]);

  // 디자인 유지 위해 변수명 그대로 사용 (추가 클라이언트 필터 없음)
  const filtered = useMemo(() => items, [items]);

  const onDelete = async (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm('해당 분석 이력을 삭제할까요?')) return;

    // 낙관적 업데이트
    const prev = items;
    setItems((ps) => ps.filter((h) => h.id !== id));
    try {
      await deleteAnalysis(id);
    } catch {
      // 롤백
      setItems(prev);
      alert('삭제 중 오류가 발생했습니다.');
    }
  };

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">분석 이력</h2>
      <p className="text-xs text-gray-500 mt-0.5">
        최근 진단명과 날짜만 간단히 보여드립니다.
      </p>

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
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
          <Filter
            size={16}
            className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400"
          />
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
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>
          <Filter
            size={16}
            className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-gray-400"
          />
        </div>
      </div>

      {/* 리스트 */}
      <div className="mt-3 divide-y divide-gray-100 rounded-2xl border border-gray-100 bg-white overflow-hidden">
        {loading && <div className="p-4 text-sm text-gray-500">불러오는 중…</div>}

        {!loading &&
          filtered.map((h) => (
            <Link
              key={h.id}
              href={`/result/${h.id}`}
              className="flex items-center gap-3 p-4 hover:bg-gray-50 transition relative"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {h.summary || h.disease_name}
                </p>
                <p className="mt-0.5 inline-flex items-center gap-1 text-xs text-gray-500">
                  <Calendar size={14} />
                  <span>{getDateStr(h)}</span>
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

        {!loading && filtered.length === 0 && (
          <div className="p-4 text-sm text-gray-500 text-center">
            조건에 맞는 분석 이력이 없습니다.
          </div>
        )}
      </div>
    </section>
  );
}
