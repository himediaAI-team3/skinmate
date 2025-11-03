import type { DiagnoseItem, LikedItem, UserProfile } from './mypage.types';

export const MOCK_USER: UserProfile = {
  avatar: '/images/2.webp',
  name: '박진우',
  email: 'jinwoopz@naver.com',
  info: [
    { label: '피부타입', value: '건성' },
    { label: '성별', value: '남성' },
    { label: '나이', value: '20대' },
  ],
};

export const MOCK_HISTORY: DiagnoseItem[] = [
  { id: 54, date: '2025-10-22', summary: '여드름' },
  { id: 53, date: '2025-10-15', summary: '건선' },
];

export const MOCK_LIKES: LikedItem[] = [
  { id: 2, brand: 'Rayderm', name: '오일프리 선스크린 SPF50+', price: 15800, image: 'https://placehold.co/320x320/B2DFDB/00796B?text=Sun', href: '/cosmetics/2' },
  { id: 1, brand: 'SKNM', name: '수딩 시카 크림', price: 19800, image: 'https://placehold.co/320x320/FFE0B2/FF6B6B?text=Cica', href: '/cosmetics/1' },
  { id: 3, brand: 'HyaLab', name: '히알루론산 토너 500ml', price: 12900, image: 'https://placehold.co/320x320/E1BEE7/6A1B9A?text=Toner', href: '/cosmetics/3' },
];
