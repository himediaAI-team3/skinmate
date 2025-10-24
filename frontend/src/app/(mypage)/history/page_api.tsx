// app/(mypage)/history/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { Calendar, Trash2, Filter } from 'lucide-react';
import { fetchDiagnosisHistory, deleteDiagnosis } from '@/app/features/history';
import type { DiagnosisSummary } from '@/app/entities/history';

// ▼ 카테고리 필터 옵션 (요청안 그대로)
const CATEGORY_OPTIONS = ['전체', '건선', '아토피', '여드름', '지루', '주사', '정상'] as const;
type CategoryOpt = typeof CATEGORY_OPTIONS[number];

const DATE_OPTIONS = ['전체', '1일전', '7일전', '한달전'] as const;
type DateOpt = typeof DATE_OPTIONS[number];

// 진단명에서 카테고리 추론 (백엔드 disease_name 기준 키워드 매핑)
function inferCategoryByDiseaseName(name: string): CategoryOpt {
  const s = (name || '').toLowerCase();
  if (s.includes('건선')) return '건선';
  if (s.includes('아토피')) return '아토피';
  if (s.includes('여드름')) return '여드름';
  if (s.includes('지루')) return '지루';
  if (s.includes('주사')) return '주사';
  if (s.includes('정상')) return '정상';
  // 매칭 안 되면 '정상'으로 처리(옵션 목록에 '기타'가 없으므로)
  return '정상';
}

// "1일전/7일전/한달전" 기준 일수
function daysFor(opt: DateOpt): number | null {
  switch (opt) {
    case '1일전': return 1;
    case '7일전': return 7;
    case '한달전': return 30;
    default: return null; // 전체
  }
}

// YYYY-MM-DD로 포맷
function fmtDate(iso: string) {
  try {
    const d = new Date(iso);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  } catch {
    return iso;
  }
}

export default function HistoryPage() {
  const [items, setItems] = useState<DiagnosisSummary[]>([]);
  const [cursor, setCursor] = useState<string | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [moreLoading, setMoreLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 필터 상태
  const [catFilter, setCatFilter] = useState<CategoryOpt>('전체');
  const [dateFilter, setDateFilter] = useState<DateOpt>('전체');

  // 최초 로드
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        setLoading(true);
        const res = await fetchDiagnosisHistory();
        if (!alive) return;
        setItems(res.data.items);
        setCursor(res.data.next_cursor ?? null);
        setError(null);
      } catch (e: any) {
        if (!alive) return;
        setError(e?.message || '진단 이력을 불러오지 못했습니다.');
      } finally {
        if (alive) setLoading(false);
      }
    })();
    return () => { alive = false; };
  }, []);

  // 더 보기 (커서 페이지네이션)
  const onLoadMore = async () => {
    if (!cursor) return;
    try {
      setMoreLoading(true);
      const res = await fetchDiagnosisHistory(cursor);
      setItems(prev => [...prev, ...res.data.items]);
      setCursor(res.data.next_cursor ?? null);
    } catch (e: any) {
      setError(e?.message || '더 불러오는 중 문제가 발생했습니다.');
    } finally {
      setMoreLoading(false);
    }
  };

  // 삭제 (낙관적 업데이트)
  const onDelete = async (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    const prev = items;
    setItems(prev.filter(h => h.analysis_id !== id));
    try {
      await deleteDiagnosis(id);
    } catch (err: any) {
      // 실패 시 복구
      setItems(prev);
      alert(err?.message || '삭제에 실패했습니다.');
    }
  };

  // 필터링
  const filtered = useMemo(() => {
    const now = new Date();
    const d = daysFor(dateFilter);
    // 날짜는 "이전 N일 내" → 오늘 날짜 기준 (시간은 무시)
    const cutoff = d
      ? new Date(now.getFullYear(), now.getMonth(), now.getDate() - d)
      : null;

    return items.filter((h) => {
      const cat = inferCategoryByDiseaseName(h.disease_name);
      const passCat = catFilter === '전체' ? true : (cat === catFilter);

      // diagnosed_at: ISO
      const passDate = !cutoff ? true : new Date(h.diagnosed_at) >= cutoff;

      return passCat && passDate;
    });
  }, [items, catFilter, dateFilter]);

  const empty = !loading && filtered.length === 0;

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">분석 이력</h2>
      <p className="text-xs text-gray-500 mt-0.5">최근 진단명과 날짜만 간단히 보여드립니다.</p>

      {/* 에러 */}
      {error && (
        <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 text-red-700 px-4 py-3">
          <p className="text-sm font-semibold">불러오기 실패</p>
          <p className="text-xs mt-0.5">{error}</p>
        </div>
      )}

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

      {/* 로딩 스켈레톤 */}
      {loading && (
        <ul className="mt-3 space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <li key={i} className="h-14 rounded-xl bg-gray-100 animate-pulse" />
          ))}
        </ul>
      )}

      {/* 리스트 */}
      {!loading && (
        <div className="mt-3 divide-y divide-gray-100 rounded-2xl border border-gray-100 bg-white overflow-hidden">
          {filtered.map((h) => (
            <Link
              key={h.analysis_id}
              href={`/result/${h.analysis_id}`}
              className="flex items-center gap-3 p-4 hover:bg-gray-50 transition relative"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {h.disease_name}
                </p>
                <p className="mt-0.5 inline-flex items-center gap-1 text-xs text-gray-500">
                  <Calendar size={14} />
                  <span>{fmtDate(h.diagnosed_at)}</span>
                </p>
              </div>

              {/* 우측: 휴지통 (화살표 제거 자리 대체) */}
              <button
                type="button"
                aria-label="이 진단 이력 삭제"
                title="삭제"
                onClick={(e) => onDelete(e, h.analysis_id)}
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

          {empty && (
            <div className="p-4 text-sm text-gray-500 text-center">
              조건에 맞는 분석 이력이 없습니다.
            </div>
          )}
        </div>
      )}

      {/* 더 보기 (커서 있을 때만) */}
      {!loading && cursor && (
        <div className="mt-3 flex justify-center">
          <button
            onClick={onLoadMore}
            disabled={moreLoading}
            className="inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-semibold hover:bg-gray-50 disabled:opacity-50"
          >
            {moreLoading ? '불러오는 중…' : '더 보기'}
          </button>
        </div>
      )}
    </section>
  );
}
