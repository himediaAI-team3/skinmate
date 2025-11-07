// ※ 상단에 'use client' 넣지 마세요.

import type { UserProfile } from './mypage.types';
import { MOCK_USER } from './mypage.mock';

const KEY = 'skinmate_profile';
const isBrowser = typeof window !== 'undefined';

export type EditableProfile = {
  name: string;
  email: string;
  avatar: string;   // 이미지 URL 또는 dataURL
  skinType: string; // 건성/지성/복합성/중성/민감성 등
  gender: string;   // 남성/여성/기타
  ageGroup: string; // '10대'/'20대'/...
};

export function loadProfile(): UserProfile {
  if (!isBrowser) return MOCK_USER; // SSR/빌드 단계
  try {
    const raw = window.localStorage.getItem(KEY);
    if (!raw) return MOCK_USER;
    const parsed = JSON.parse(raw) as Partial<EditableProfile>;
    return toUserProfile({
      name: parsed.name ?? '',
      email: parsed.email ?? '',
      avatar: parsed.avatar ?? '',
      skinType: parsed.skinType ?? '',
      gender: parsed.gender ?? '',
      ageGroup: parsed.ageGroup ?? '',
    });
  } catch {
    return MOCK_USER;
  }
}

export function saveProfile(editable: EditableProfile): UserProfile {
  if (isBrowser) {
    try {
      window.localStorage.setItem(KEY, JSON.stringify(editable));
    } catch {/* ignore */}
  }
  return toUserProfile(editable);
}

function toUserProfile(e: Partial<EditableProfile>): UserProfile {
  return {
    avatar: e.avatar && e.avatar.length > 0 ? e.avatar : MOCK_USER.avatar,
    name:   e.name && e.name.length > 0 ? e.name : MOCK_USER.name,
    email:  e.email && e.email.length > 0 ? e.email : MOCK_USER.email,
    info: [
      { label: '피부타입', value: e.skinType && e.skinType.length > 0 ? e.skinType : '미입력' },
      { label: '성별',     value: e.gender   && e.gender.length   > 0 ? e.gender   : '미입력' },
      { label: '나이',     value: e.ageGroup && e.ageGroup.length > 0 ? e.ageGroup : '미입력' },
    ],
  };
}

// 초기값 생성 헬퍼 (MOCK_USER → EditableProfile)
export function toEditable(p: UserProfile): EditableProfile {
  const skinType = p.info.find(i => i.label === '피부타입')?.value ?? '';
  const gender   = p.info.find(i => i.label === '성별')?.value ?? '';
  const ageGroup = p.info.find(i => i.label === '나이')?.value ?? '';
  return {
    name: p.name,
    email: p.email,
    avatar: p.avatar,
    skinType,
    gender,
    ageGroup,
  };
}
