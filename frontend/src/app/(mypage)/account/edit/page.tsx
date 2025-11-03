'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { loadProfile, /* saveProfile, */ toEditable, type EditableProfile } from '@/lib/mypage.store';

const SKIN_TYPES = ['건성', '지성', '복합성', '민감성'] as const;
const GENDER_TYPES = ['남성', '여성', '기타'] as const;
const AGE_GROUPS = ['10대', '20대', '30대', '40대', '50대', '60대'] as const;

export default function EditAccountPage() {
  const router = useRouter();
  const [form, setForm] = useState<EditableProfile>({
    name: '',
    email: '',
    avatar: '',
    skinType: '',
    gender: '',
    ageGroup: '',
  });

  useEffect(() => {
    const p = loadProfile();
    setForm(toEditable(p));
  }, []);

  const onChange = (field: keyof EditableProfile, value: string) =>
    setForm(prev => ({ ...prev, [field]: value }));

  const onFile = async (file?: File | null) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setForm(prev => ({ ...prev, avatar: reader.result as string }));
      }
    };
    reader.readAsDataURL(file);
  };

  // ⬇⬇ 여기만 변경됨: 저장 눌러도 알림만 띄우고 실제 저장/이동 안 함
  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('아직 준비중인 기능입니다. 곧 업데이트될 예정이에요!');
    // saveProfile(form);
    // router.push('/account');
  };

  return (
    <main className="px-5 py-6 max-w-xl mx-auto">
      <h1 className="text-xl font-extrabold text-gray-900">정보 수정</h1>

      <form onSubmit={onSubmit} className="mt-5 space-y-6">
        {/* 이미지 */}
        <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-bold text-gray-900">프로필 이미지</h2>
          <div className="mt-3 flex items-center gap-4">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={form.avatar || '/images/2.webp'}
              alt="미리보기"
              className="w-20 h-20 rounded-2xl object-cover ring-4 ring-white border border-gray-200 shadow"
            />
            <div className="space-y-2 w-full">
              <label className="block">
                <span className="text-xs font-semibold text-gray-600">이미지 파일 업로드</span>
                <input
                  type="file"
                  accept="image/*"
                  className="mt-1 block w-full text-sm"
                  onChange={(e) => onFile(e.target.files?.[0])}
                />
              </label>
            </div>
          </div>
        </section>

        {/* 기본 정보 */}
        <section className="rounded-2xl border border-gray-100 bg-white p-4 shadow-sm">
          <h2 className="text-sm font-bold text-gray-900">기본 정보</h2>
          <div className="mt-3 grid grid-cols-1 gap-3">
            <label className="block">
              <span className="text-xs font-semibold text-gray-600">이름</span>
              <input
                type="text"
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm"
                value={form.name}
                onChange={(e) => onChange('name', e.target.value)}
                required
              />
            </label>

            <label className="block">
              <span className="text-xs font-semibold text-gray-600">이메일</span>
              <input
                type="email"
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm"
                value={form.email}
                onChange={(e) => onChange('email', e.target.value)}
                required
              />
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
                value={form.skinType}
                onChange={(e) => onChange('skinType', e.target.value)}
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
                value={form.gender}
                onChange={(e) => onChange('gender', e.target.value)}
                required
              >
                <option value="" disabled>선택</option>
                {GENDER_TYPES.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </label>

            <label className="block">
              <span className="text-xs font-semibold text-gray-600">나이</span>
              <select
                className="mt-1 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm bg-white"
                value={form.ageGroup}
                onChange={(e) => onChange('ageGroup', e.target.value)}
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
          >
            저장
          </button>
        </div>
      </form>
    </main>
  );
}
