import { http } from '@/lib/http';
import { UpdateSkinInfoInput, UpdateSkinInfoOutput } from '@/entities/info';

export const infoApi = {
  update: async (memberId: number, input: typeof UpdateSkinInfoInput._type) =>
    UpdateSkinInfoOutput.parse(
      await http(
        `http://192.168.0.235:8000/api/members/${memberId}`,
        {
          method: 'PUT',
          json: UpdateSkinInfoInput.parse(input),
          // withAuth 기본값이 true라 생략 가능 (명시하고 싶으면 주석 해제)
          // withAuth: true,
        }
      )
    ),
};
