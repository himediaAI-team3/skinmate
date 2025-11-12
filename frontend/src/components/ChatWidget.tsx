'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { sendChatMessage } from '@/features/chat';

type Msg = { role: 'user' | 'assistant'; text: string };

const ICON = '/chatbot.svg'; // public 폴더 아이콘

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: 'assistant', text: '안녕하세요! 스킨케어 도우미입니다! 무엇을 도와드릴까요?' },
  ]);
  const [input, setInput] = useState('');
  const [threadId, setThreadId] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
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

  const send = async () => {
    if (!input.trim() || loading) return;
    
    const userMessage = input.trim();
    const userMsg: Msg = { role: 'user', text: userMessage };
    setMsgs((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage, threadId);
      
      // thread_id 저장 (다음 대화에서 사용)
      if (response.thread_id) {
        setThreadId(response.thread_id);
      }

      const assistantMsg: Msg = {
        role: 'assistant',
        text: response.response,
      };
      setMsgs((m) => [...m, assistantMsg]);
    } catch (error) {
      console.error('채팅 오류:', error);
      const errorMsg: Msg = {
        role: 'assistant',
        text: '챗봇을 이용하시려면 로그인이 필요합니다.',
      };
      setMsgs((m) => [...m, errorMsg]);
    } finally {
      setLoading(false);
    }
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
                disabled={loading}
                className="flex-1 rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
              />
              <button
                onClick={send}
                disabled={loading}
                className="rounded-xl bg-gray-900 text-white px-3 py-2 text-sm font-semibold hover:opacity-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '전송 중...' : '전송'}
              </button>
            </div>
            {loading && (
              <p className="mt-1 text-[10px] text-gray-500">
                AI가 답변을 생성하고 있습니다...
              </p>
            )}
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
