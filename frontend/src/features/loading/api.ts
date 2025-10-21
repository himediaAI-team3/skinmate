import { SkinAnalysisOutput } from '@/entities/loading';
import { http } from '@/lib/http';

// 업로드+LLM 동기 실행: POST /api/skin-analysis (FormData: member_id, image)
// 결과가 나올 때까지 서버가 처리한 뒤 SkinAnalysisOutput 반환
async function submit(memberId: number, file: File) {
  const form = new FormData();
  form.append('member_id', String(memberId));
  form.append('image', file);

  // http 래퍼가 FormData 지원 안하면 fetch 사용
  const res = await fetch('http://192.168.0.235:8000/api/skin-analysis', { method: 'POST', body: form });
  const json = await res.json();
  return SkinAnalysisOutput.parse(json);
}

// 결과 조회: GET /api/skin-analysis/:analysis_id
async function get(analysisId: number) {
  return SkinAnalysisOutput.parse(
    await http(`http://192.168.0.235:8000/api/skin-analysis/${analysisId}`, { method: 'GET' })
  );
}

export const analysisApi = { submit, get };