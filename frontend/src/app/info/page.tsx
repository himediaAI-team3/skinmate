'use client';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { SkinTypeEnum } from '@/entities/info';

const SKIN_TYPES = SkinTypeEnum.options;

type SkinType = typeof SKIN_TYPES[number];

export default function InfoPage() {
  const router = useRouter();
  const [form, setForm] = useState<{
    skinType: SkinType | '';
    priceMin: string;
    priceMax: string;
  }>({ skinType: '', priceMin: '', priceMax: '' });

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const toggle = <K extends 'skinType'>(k: K, v: any) =>
    setForm(p => ({ ...p, [k]: p[k] === v ? '' : v }));

  const onNum = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target; // priceMin | priceMax
    setForm(p => ({ ...p, [id]: value }));
  };

  const validate = () => {
    if (!form.skinType) return '피부 타입을 선택해주세요.';
    const min = Number(form.priceMin ?? 0);
    const max = Number(form.priceMax ?? 0);
    if (!Number.isFinite(min) || !Number.isFinite(max)) return '가격은 숫자여야 합니다.';
    if (min <= 0 || max <= 0) return '가격은 0보다 커야 합니다.';
    if (min > max) return '최소 금액이 최대 금액보다 클 수 없습니다.';
    return null;
  };

  const handleNext = async () => {
    setMsg(null);
    const err = validate();
    if (err) return setMsg(err);

    setLoading(true);
    try {
      // member 업데이트 없이 sessionStorage에 정보만 저장
      const skinInfo = {
        skin_type: form.skinType as SkinType,
        min_price: Number(form.priceMin),
        max_price: Number(form.priceMax),
      };
      sessionStorage.setItem('skinMateSkinInfo', JSON.stringify(skinInfo));
      router.push('/upload');
    } catch (e: any) {
      setMsg(e?.message ?? '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const btn = (on: boolean) =>
    `border-2 rounded-xl p-4 text-center font-semibold transition-colors
     ${on ? 'border-orange-500 bg-orange-100 text-orange-700' : 'border-gray-200 text-gray-700 hover:border-orange-200'}`;

  return (
    <div>
      <header className="p-4 flex items-center h-16">
        <h1 className="text-xl font-bold text-gray-800 absolute left-1/2 -translate-x-1/2">추가 정보 입력</h1>
      </header>
        <main className="p-6">
        {/* 피부 타입 */}
        <section className="bg-orange-50 p-6 rounded-2xl">
          <h3 className="text-xl font-bold text-gray-800">피부 타입</h3>
          <p className="text-gray-500 mt-1">해당하는 피부 타입을 선택해주세요.</p>
          <div className="grid grid-cols-2 gap-4 mt-3">
            {SKIN_TYPES.map(t => (
              <button key={t} type="button" onClick={() => toggle('skinType', t)} className={btn(form.skinType === t)}>
                {t}
              </button>
            ))}
          </div>
        </section>

        {/* 가격대 */}
        <section className="bg-orange-50 p-6 rounded-2xl mt-6">
          <h3 className="text-xl font-bold text-gray-800">가격대</h3>
          <p className="text-gray-500 mt-1">원하시는 화장품의 가격 범위를 입력해주세요.</p>
          <div className="grid grid-cols-2 gap-4 mt-4">
            <div className="flex items-center border-2 border-gray-200 rounded-xl p-3 focus-within:border-orange-500 transition-colors">
              <input type="number" id="priceMin" placeholder="최소 금액" value={form.priceMin} onChange={onNum}
                     className="w-full font-semibold text-gray-700 focus:outline-none bg-transparent" min={0}/>
              <span className="font-semibold text-gray-500 ml-2">원</span>
            </div>
            <div className="flex items-center border-2 border-gray-200 rounded-xl p-3 focus-within:border-orange-500 transition-colors">
              <input type="number" id="priceMax" placeholder="최대 금액" value={form.priceMax} onChange={onNum}
                     className="w-full font-semibold text-gray-700 focus:outline-none bg-transparent" min={0}/>
              <span className="font-semibold text-gray-500 ml-2">원</span>
            </div>
          </div>
        </section>

        {msg && <p className="mt-4 text-sm text-red-600">{msg}</p>}

        <div className="px-6 pt-6 bg-white">
          <button
            onClick={handleNext}
            disabled={loading}
            className="w-full bg-orange-500 text-white font-bold py-4 rounded-full shadow-lg hover:bg-orange-600 transition-colors disabled:opacity-50"
          >
            {loading ? '저장 중...' : '다음'}
          </button>
        </div>

        {/* 탭바와의 간격 확보를 위한 스페이서 */}
        <div aria-hidden />
      </main>
    </div>
  );
}
