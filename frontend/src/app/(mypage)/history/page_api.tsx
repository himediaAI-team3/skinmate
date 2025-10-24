// app/(mypage)/history/page.tsx
'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { ChevronRight, Clock } from 'lucide-react';
import { fetchDiagnosisHistory } from '@/app/features/history';
import type { DiagnosisSummary } from '@/app/entities/history';

// YYYY-MM-DD 포맷
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

  const empty = useMemo(() => !loading && items.length === 0, [loading, items.length]);

  return (
    <section className="mt-2">
      <h2 className="text-lg font-bold text-gray-900">진단 이력</h2>
      <p className="text-xs text-gray-500 mt-0.5">최근 진단 순으로 표시됩니다.</p>

      {error && (
        <div className="mt-3 rounded-2xl border border-red-200 bg-red-50 text-red-700 px-4 py-3">
          <p className="text-sm font-semibold">불러오기 실패</p>
          <p className="text-xs mt-0.5">{error}</p>
        </div>
      )}

      {loading && (
        <ul className="mt-3 space-y-2">
          {Array.from({ length: 5 }).map((_, i) => (
            <li key={i} className="h-14 rounded-xl bg-gray-100 animate-pulse" />
          ))}
        </ul>
      )}

      {empty && (
        <div className="mt-3 rounded-2xl border border-dashed border-gray-200 p-6 text-center text-sm text-gray-500">
          아직 진단 이력이 없습니다.
        </div>
      )}

      {!loading && items.length > 0 && (
        <ul className="mt-3 divide-y divide-gray-100 rounded-2xl border border-gray-100 bg-white overflow-hidden">
          {items.map((it) => (
            <li key={it.analysis_id}>
              <Link
                href={`/result/${it.analysis_id}`}
                className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-gray-900 truncate">{it.disease_name}</p>
                  <p className="mt-0.5 inline-flex items-center gap-1 text-[11px] font-medium text-gray-500">
                    <Clock size={12} /> {fmtDate(it.diagnosed_at)}
                  </p>
                </div>
                <ChevronRight size={18} className="text-gray-400 flex-shrink-0" />
              </Link>
            </li>
          ))}
        </ul>
      )}

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
