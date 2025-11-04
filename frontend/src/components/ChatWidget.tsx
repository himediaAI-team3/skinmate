'use client';

import { useEffect, useMemo, useRef, useState } from 'react';

type Msg = { role: 'user' | 'assistant'; text: string };

const ICON = '/chatbot.svg'; // public 폴더 아이콘

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: 'assistant', text: '안녕하세요! 스킨케어 도우미입니다! 무엇을 도와드릴까요?' },
  ]);
  const [input, setInput] = useState('');
  const bodyRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // AppHeader( max-w-md + px-7 ) 우측 정렬 규칙
  const rightRule = useMemo(
    () => ({
      right: 'max(12px, calc((100vw - 28rem) / 2 + 1.75rem))',
    }),
    []
  );

  useEffect(() => {
    bodyRef.current?.scrollTo({ top: bodyRef.current.scrollHeight });
    if (open) inputRef.current?.focus();
  }, [open, msgs.length]);

  useEffect(() => {
    if (!open) return;
    const onEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', onEsc);
    return () => window.removeEventListener('keydown', onEsc);
  }, [open]);

  const send = () => {
    if (!input.trim()) return;
    const userMsg: Msg = { role: 'user', text: input.trim() };
    setMsgs((m) => [...m, userMsg]);

    const reply: Msg = {
      role: 'assistant',
      text:
        '메모했어요! 😊\n- 실제 연결 전까지는 데모 응답을 보여드려요.\n- “내 피부타입에 맞는 토너 추천” 처럼 질문해보세요.',
    };
    setTimeout(() => setMsgs((m) => [...m, reply]), 200);
    setInput('');
  };

  const onKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') send();
  };

  // iOS 안전영역 하단 패딩
  const safeBottom = 'env(safe-area-inset-bottom, 0px)';

  // 👉 오른쪽으로 더 이동시키는 픽셀(양수 = 우측으로)
  const offsetX = 10; // 필요시 6, 12 등으로 조정

  return (
    <>
      {/* 플로팅 버튼 (영역 자체 이동) */}
      <button
        type="button"
        aria-label="챗봇 열기"
        onClick={() => setOpen(true)}
        className={[
          'fixed z-[70] bottom-[56px]',
          'rounded-full shadow-lg border border-orange-100',
          'bg-white w-12 h-12 flex items-center justify-center',
          'hover:shadow-xl transition',
        ].join(' ')}
        style={{ ...rightRule, transform: `translateX(${offsetX}px)` }}
      >
        <div className="relative">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={ICON} alt="챗봇" width={24} height={24} />
          <span
            className="absolute top-0 right-0 transform translate-x-[20px] -translate-y-[10px]
                       text-[10px] rounded-full bg-orange-500 text-white px-1 py-5.5
                       shadow pointer-events-none"
          >
            Beta
          </span>
        </div>
      </button>

      {/* 챗 패널 (영역 자체 이동 + 폭/높이 축소) */}
      <div
        role="dialog"
        aria-modal="true"
        className={['fixed z-[70]', open ? 'pointer-events-auto' : 'pointer-events-none'].join(' ')}
        style={{
          ...rightRule,
          transform: `translateX(${offsetX}px)`,
          bottom: `calc(120px + ${safeBottom})`,
          width: 'min(100vw - 24px, 24rem)',
        }}
      >
        <div
          className={[
            'rounded-2xl border border-gray-200 bg-white shadow-2xl',
            'transition-all duration-200',
            open ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-3',
            'flex flex-col overflow-hidden',
          ].join(' ')}
          style={{ height: 'min(60vh, 520px)' }}
        >
          {/* 헤더 */}
          <div className="h-11 px-3 bg-gradient-to-r from-orange-50 to-pink-50 border-b flex items-center justify-between">
            <div className="flex items-center gap-2">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={ICON} alt="" width={18} height={18} aria-hidden />
              <p className="text-sm font-semibold text-gray-800">챗봇</p>
            </div>
            <button
              className="text-xs text-gray-600 hover:text-gray-900"
              onClick={() => setOpen(false)}
            >
              닫기
            </button>
          </div>

          {/* 본문 */}
          <div ref={bodyRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2">
            {msgs.map((m, i) => (
              <div key={i} className={m.role === 'user' ? 'text-right' : 'text-left'}>
                <div
                  className={[
                    'inline-block px-3 py-2 rounded-2xl text-[13px] leading-5',
                    m.role === 'user'
                      ? 'bg-gray-900 text-white rounded-br-sm'
                      : 'bg-gray-100 text-gray-800 rounded-bl-sm',
                  ].join(' ')}
                >
                  {m.text.split('\n').map((line, idx) => (
                    <span key={idx} className="block">
                      {line}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* 입력 */}
          <div className="border-t p-2 bg-white">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={onKey}
                placeholder="무엇을 도와드릴까요?"
                className="flex-1 rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-200"
              />
              <button
                onClick={send}
                className="rounded-xl bg-gray-900 text-white px-3 py-2 text-sm font-semibold hover:opacity-95"
              >
                전송
              </button>
            </div>
            <p className="mt-1 text-[10px] text-gray-500">
              ※ 데모 버전입니다. 이후 실제 AI 응답으로 교체할 수 있어요.
            </p>
          </div>
        </div>
      </div>

      {/* 배경 딤 */}
      {open && (
        <div
          className="fixed inset-0 z-[60] bg-black/10 backdrop-blur-[1px]"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  );
}
