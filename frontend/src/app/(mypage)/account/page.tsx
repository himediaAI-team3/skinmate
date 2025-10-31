'use client';

import { useState } from 'react';
import { Mail, User2, Info } from 'lucide-react';
import { MOCK_USER } from '@/lib/mypage.mock';

const GENDER_TYPES = ['남성', '여성', '기타'] as const;
const AGE_GROUPS = [10, 20, 30, 40, 50, 60] as const;

type Gender = (typeof GENDER_TYPES)[number] | null;
type AgeGroup = (typeof AGE_GROUPS)[number] | null;

export default function AccountPage() {
  const [form, setForm] = useState<{ gender: Gender; ageGroup: AgeGroup }>({
    gender: null,
    ageGroup: null,
  });

  const toggle = (field: 'gender' | 'ageGroup', value: any) =>
    setForm((prev) => ({
      ...prev,
      [field]: prev[field] === value ? null : value,
    }));

  const btn = (active: boolean) =>
    `w-full rounded-xl border px-4 py-3 text-sm font-semibold transition
     ${active ? 'bg-gray-900 text-white border-gray-900' : 'bg-white text-gray-800 border-gray-200 hover:bg-gray-50'}`;

  return (
    <>
      <section className="mt-2">
        <div className="overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm">
          {/* 상단 비주얼 배너 */}
          <div
            className="h-24 w-full"
            style={{
              background:
                'radial-gradient(1000px 200px at -10% -40%, rgba(255,152,0,.18), transparent 60%), radial-gradient(800px 200px at 110% -40%, rgba(236,64,122,.18), transparent 60%), linear-gradient(135deg, rgba(255,255,255,1) 0%, rgba(255,255,255,.6) 100%)',
            }}
          />

          {/* 헤더 블록 (아바타 오버랩) */}
          <div className="px-5 pb-5 -mt-10">
            <div className="flex items-end gap-4">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={MOCK_USER.avatar}
                alt={`${MOCK_USER.name} 프로필`}
                className="w-20 h-20 rounded-2xl object-cover ring-4 ring-white border border-gray-200 shadow"
              />

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <User2 size={16} className="text-gray-500" />
                  <p className="text-[15px] font-extrabold tracking-tight text-gray-900">
                    {MOCK_USER.name}
                  </p>
                </div>
                <div className="mt-1 flex items-center gap-2 text-gray-700">
                  <Mail size={16} className="text-gray-500" />
                  <p className="text-sm truncate">{MOCK_USER.email}</p>
                </div>
              </div>

              {/*
              <Link
                href="/mypage/edit"
                className="rounded-full px-3 py-1.5 text-xs font-semibold bg-gray-900 text-white shadow-sm hover:opacity-95"
              >
                정보 수정
              </Link>
              */}
            </div>
          </div>

          {/* 정보 타일 섹션 */}
          <div className="px-5 pb-5">
            <h2 className="text-sm font-bold text-gray-900">내 정보</h2>

            <div className="mt-3 grid grid-cols-2 gap-3">
              {MOCK_USER.info.map((it: any, i: number) => (
                <div
                  key={i}
                  className="rounded-xl border border-gray-100 bg-white p-3 shadow-[0_1px_0_rgba(0,0,0,0.03)]"
                >
                  <div className="flex items-center gap-1.5 text-[11px] font-semibold text-gray-500">
                    <Info size={12} className="text-gray-400" />
                    {it.label}
                  </div>
                  <div className="mt-1 text-sm font-medium text-gray-900">{it.value}</div>
                </div>
              ))}
            </div>

            <div className="mt-5 border-t border-gray-100 pt-3" />
          </div>
        </div>
      </section>

      <section className="bg-orange-50 p-6 rounded-2xl mt-6">
        <h3 className="text-xl font-bold text-gray-800">성별</h3>
        <div className="grid grid-cols-2 gap-4 mt-3">
          {GENDER_TYPES.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => toggle('gender', t)}
              className={btn(form.gender === t)}
            >
              {t}
            </button>
          ))}
        </div>
      </section>

      <section className="bg-orange-50 p-6 rounded-2xl mt-6">
        <h3 className="text-xl font-bold text-gray-800">나이</h3>
        <div className="grid grid-cols-3 gap-3 mt-3">
          {AGE_GROUPS.map((a) => (
            <button
              key={a}
              type="button"
              onClick={() => toggle('ageGroup', a)}
              className={btn(form.ageGroup === a)}
            >
              {a}대
            </button>
          ))}
        </div>
      </section>
    </>
  );
}
