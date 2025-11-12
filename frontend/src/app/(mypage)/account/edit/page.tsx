'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import type { MemberResponse } from '@/entities/account';
import { getMe, updateMe, getDefaultAvatar } from '@/features/account/api';

const SKIN_TYPES = ['건성', '지성', '복합성', '민감성'] as const;
const GENDER_TYPES = ['남성', '여성', '기타'] as const;
const AGE_GROUPS = [10, 20, 30, 40, 50, 60] as const;

export default function EditAccountPage() {
  const router = useRouter();
  const [me, setMe] = useState<MemberResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // 폼 상태
  const [name, setName] = useState('');
  const [skinType, setSkinType] = useState('');
  const [gender, setGender] = useState('');
  const [ageGroup, setAgeGroup] = useState<number | ''>('');

  useEffect(() => {
    (async () => {
      try {
        const data = await getMe();
        setMe(data ?? null);
        setName(data?.name ?? '');
        setSkinType(data?.skin_type ?? '');
        setGender(data?.gender ?? '');
        setAgeGroup(data?.age_group ?? '');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const avatar = getDefaultAvatar(me?.gender);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateMe({
        name: name || null,
        skin_type: skinType || null,
        gender: gender || null,
        age_group: typeof ageGroup === 'number' ? ageGroup : null,
      });
      alert('저장되었습니다.');
      router.push('/account');
    } catch (err) {
      alert('저장 중 오류가 발생했습니다.');
    }
  };

  return (
    <main className="px-5 py-6 max-w-xl mx-auto">
      <h1 className="text-xl font-extrabold text-gray-900">정보 수정</h1>

      <form onSubmit={onSubmit} className="mt-5 space-y-6">
        {/* 이미지(현재는 서버 저장 미구현: 프리뷰만) */}
        <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-bold text-gray-900">프로필 이미지</h2>
          <div className="mt-3 flex items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={avatar}
              alt="미리보기"
              className="w-20 h-20 rounded-2xl object-cover ring-4 ring-white border border-gray-200 shadow"
            />
            <div className="text-xs text-gray-500">
              현재는 성별에 따라 기본 이미지가 표시됩니다.
            </div>
          </div>
        </section>

        {/* 기본 정보 */}
        <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-bold text-gray-900">기본 정보</h2>
          <div className="mt-3 grid grid-cols-1 gap-3">
          <label className="block">
            <span className="text-xs font-semibold text-gray-600">이름</span>
            <div
              className={[
                'mt-1 w-full text-sm text-gray-900',
                'px-1 py-2',           // 인풋과 비슷한 세로 리듬 유지
                'cursor-default select-text',
              ].join(' ')}
              aria-readonly="true"
              title="읽기 전용"
            >
              {name || <span className="text-gray-400 italic">이름 미입력</span>}
            </div>
          </label>
          </div>
        </section>
        {/* 상세 프로필 */}
        <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-bold text-gray-900">프로필 상세</h2>
          <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
            <label className="block">
              <span className="text-xs font-semibold text-gray-600">피부타입</span>
              <select
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm bg-white"
                value={skinType}
                onChange={(e) => setSkinType(e.target.value)}
                required
              >
                <option value="" disabled>선택</option>
                {SKIN_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </label>

            <label className="block">
              <span className="text-xs font-semibold text-gray-600">성별</span>
              <select
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm bg-white"
                value={gender}
                onChange={(e) => setGender(e.target.value)}
                required
              >
                <option value="" disabled>선택</option>
                {GENDER_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </label>

            <label className="block">
              <span className="text-xs font-semibold text-gray-600">나이대</span>
              <select
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm bg-white"
                value={ageGroup === '' ? '' : String(ageGroup)}
                onChange={(e) => setAgeGroup(e.target.value ? Number(e.target.value) : '')}
                required
              >
                <option value="" disabled>선택</option>
                {AGE_GROUPS.map(a => <option key={a} value={a}>{a}</option>)}
              </select>
            </label>
          </div>
        </section>

        <div className="flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={() => router.back()}
            className="rounded-xl border border-gray-200 bg-white px-4 py-2 text-sm font-semibold hover:bg-gray-50"
          >
            취소
          </button>
          <button
            type="submit"
            className="rounded-xl bg-gray-900 text-white px-4 py-2 text-sm font-semibold hover:opacity-95"
            disabled={loading}
          >
            저장
          </button>
        </div>
      </form>
    </main>
  );
}
