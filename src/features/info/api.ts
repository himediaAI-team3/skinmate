import { http } from '@/lib/http';
import { UpdateSkinInfoInput, UpdateSkinInfoOutput } from '@/entities/info';

export const infoApi = {
  update: async (memberId: number, input: typeof UpdateSkinInfoInput._type) =>
    UpdateSkinInfoOutput.parse(
      await http(`http://192.168.0.235:8000/api/members/${memberId}/skin-info`, {
        method: 'PATCH',
        json: UpdateSkinInfoInput.parse(input),
      })
    ),
};
