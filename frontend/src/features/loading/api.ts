import { SkinAnalysisOutput } from '@/entities/loading';
import { http } from '@/lib/http';

const API = 'http://192.168.0.235:8000';

// 결과 조회: GET /api/skin-analysis/:analysis_id
export async function get(analysisId: number) {
  return SkinAnalysisOutput.parse(
    await http(`${API}/api/skin-analysis/${analysisId}`, { method: 'GET' })
  );
}

// 업로드+LLM: POST 후 받은 analysis_id로 바로 GET까지 이어서 실행
export async function submit(memberId: number, file: File) {
  const form = new FormData();
  form.append('member_id', String(memberId));
  form.append('image', file);

  const res = await fetch(`${API}/api/skin-analysis`, { method: 'POST', body: form });
  const json = await res.json();
  // console.log("json: ", json);

  const id = json?.data?.analysis_id;
  if (!id) throw new Error('POST 응답에 analysis_id가 없습니다.');

  try {
    // 바로 한 번 시도
    return await get(id);
  } catch (e) {
    // 서버 반영 지연 대비, 아주 짧게 한 번만 재시도 (필요 없으면 이 블록 삭제)
    await new Promise(r => setTimeout(r, 800));
    return await get(id);
  }
}

export const analysisApi = { submit, get };
