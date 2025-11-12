// 사용자 프로필 타입(백엔드 응답 기준)
export type MemberResponse = {
    member_id: number;
    name?: string | null;
    email?: string | null;        // 백엔드가 내려주면 사용
    skin_type?: string | null;
    gender?: string | null;       // '남성' | '여성' | 기타
    age_group?: number | null;    // 10 | 20 | 30 ...
    created_at?: string | null;
    updated_at?: string | null;
  };
  
  // 수정용 DTO (백엔드 요청 키에 맞춤)
  export type MemberUpdateDTO = {
    skin_type?: string | null;
    gender?: string | null;
    age_group?: number | null;
    name?: string | null;
    // email은 보통 수정 안 하지만 필요시 추가
  };
  