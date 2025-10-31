import { http } from '@/lib/http';
import { z } from 'zod';

const LoginInput = z.object({ email: z.string().email(), password: z.string().min(8) });
const LoginOutput = z.object({ token: z.string() });

export type LoginInput = z.infer<typeof LoginInput>;
export const authApi = {
  login: async (data: LoginInput) =>
    LoginOutput.parse(await http('/api/auth/login', { method: 'POST', json: LoginInput.parse(data) })),
  logout: async () => http<void>('/api/auth/logout', { method: 'POST' }),
};

