'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

const PageHeader = ({ title, backHref }: { title: string; backHref: string }) => (
  <header className="p-4 flex items-center h-16">
    <a href={backHref} className="w-10 h-10 flex items-center justify-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24" height="24" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" strokeWidth="2"
        strokeLinecap="round" strokeLinejoin="round"
      >
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </a>
    <h1 className="text-xl font-bold text-gray-800 absolute left-1/2 -translate-x-1/2">
      {title}
    </h1>
  </header>
);

export default function UploadPage() {
  const router = useRouter();
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 안드로이드에서 갤러리 선택을 더 강하게 유도
  useEffect(() => {
    const ua = typeof navigator !== 'undefined' ? navigator.userAgent || '' : '';
    const isAndroid = /Android/i.test(ua);
    if (isAndroid && fileInputRef.current) {
      fileInputRef.current.setAttribute('capture', 'filesystem');
    }
  }, []);

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!f.type.startsWith('image/')) return alert('이미지 파일만 업로드할 수 있습니다.');
    if (f.size > 20 * 1024 * 1024) return alert('이미지 용량이 큽니다. 20MB 이하로 업로드해주세요.');
    setFileName(f.name);

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result as string;
      setImagePreview(base64);
      const payload = { member_id: 1, image_data_url: base64, file_name: f.name }; // TODO: 실제 member_id로 교체
      sessionStorage.setItem('skinMatePendingUpload', JSON.stringify(payload));
    };
    reader.readAsDataURL(f);

    // 같은 파일 재선택 허용
    e.currentTarget.value = '';
  };

  const onStart = async () => {
    if (loading) return;
    if (!imagePreview) return alert('피부 사진을 등록해주세요.');
    setLoading(true);
    router.push('/loading');
  };

  return (
    <div className="max-w-md mx-auto bg-white">
      <PageHeader title="사진 등록" backHref="/info" />

      <main className="p-6">
        <h2 className="text-2xl font-bold text-gray-800">
          마지막 단계예요.<br />피부 사진을 등록해주세요.
        </h2>
        <p className="text-gray-500 mt-2">
          정확한 진단을 위해 가장 선명한 사진을 올려주세요.
        </p>

        <div
          className="mt-8 w-full aspect-square bg-gray-100 rounded-2xl flex items-center justify-center cursor-pointer overflow-hidden"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"          // ← capture 제거(카메라 강제 방지)
            className="hidden"
            onChange={onChange}
          />

          {imagePreview ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={imagePreview}
              alt="Uploaded skin preview"
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex flex-col items-center justify-center text-gray-500">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48" height="48" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="1.5"
                strokeLinecap="round" strokeLinejoin="round"
              >
                <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7"></path>
                <line x1="16" x2="22" y1="5" y2="5"></line>
                <line x1="19" x2="19" y1="2" y2="8"></line>
                <circle cx="9" cy="9" r="2"></circle>
                <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path>
              </svg>
              <p className="mt-2 font-semibold text-center">
                사진을 추가하려면<br />여기를 탭하세요.
              </p>
              <p className="text-sm mt-1">갤러리에서 선택</p>
            </div>
          )}
        </div>

        {/* CTA: 일반 흐름으로 배치(고정/스티키 아님) */}
        <div className="px-6 pt-4 bg-white">
          <button
            onClick={onStart}
            disabled={!imagePreview || loading}
            className="w-full bg-orange-500 text-white font-bold py-4 rounded-full shadow-lg hover:bg-orange-600 transition-colors disabled:bg-gray-300"
          >
            {loading ? '이동 중...' : '분석 시작하기'}
          </button>
        </div>

        {/* 탭바와의 간격 확보 스페이서 */}
        <div aria-hidden />
      </main>
    </div>
  );
}