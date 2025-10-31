import { http } from '@/lib/http';
import { z } from 'zod';

export const User = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
});
export type User = z.infer<typeof User>;

export const userApi = {
  me: async () => User.parse(await http<User>('/api/users/me')),
  list: async () => z.array(User).parse(await http<User[]>('/api/users')),
  updateName: async (name: string) =>
    User.parse(await http<User>('/api/users/me', { method: 'PATCH', json: { name } })),
};

