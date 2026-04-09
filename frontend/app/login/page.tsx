'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import { auth } from '@/lib/api';
import { useAuthStore } from '@/lib/store';

type Tab = 'login' | 'register';

export default function LoginPage() {
  const router = useRouter();
  const { setToken, setUser } = useAuthStore();

  const [tab, setTab] = useState<Tab>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  function saveToken(token: string) {
    localStorage.setItem('sw_token', token);
    Cookies.set('sw_token', token, { expires: 7, path: '/' });
    setToken(token);
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await auth.login(email, password);
      saveToken(res.data.access_token);
      setUser({ email });
      router.push('/wardrobe');
    } catch {
      setError('邮箱或密码错误，请重试');
    } finally {
      setLoading(false);
    }
  }

  async function handleRegister(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }
    setLoading(true);
    try {
      await auth.register(email, password);
      const res = await auth.login(email, password);
      saveToken(res.data.access_token);
      setUser({ email });
      router.push('/wardrobe');
    } catch (err: unknown) {
      const status = (err as { response?: { status?: number } })?.response?.status;
      if (status === 400) {
        setError('该邮箱已注册，请直接登录');
      } else {
        setError('注册失败，请稍后再试');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-warm-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo / App name */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-warm-200 mb-4">
            <span className="text-3xl">👗</span>
          </div>
          <h1 className="text-2xl font-semibold text-warm-800">智能衣橱 AI</h1>
          <p className="text-warm-500 text-sm mt-1">让 AI 帮你搭配每日穿搭</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-warm-100 overflow-hidden">
          {/* Tabs */}
          <div className="flex">
            <button
              onClick={() => { setTab('login'); setError(''); }}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                tab === 'login'
                  ? 'bg-warm-600 text-white'
                  : 'bg-warm-50 text-warm-600 hover:bg-warm-100'
              }`}
            >
              登录
            </button>
            <button
              onClick={() => { setTab('register'); setError(''); }}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${
                tab === 'register'
                  ? 'bg-warm-600 text-white'
                  : 'bg-warm-50 text-warm-600 hover:bg-warm-100'
              }`}
            >
              注册
            </button>
          </div>

          <div className="p-6">
            {/* Error */}
            {error && (
              <div className="mb-4 px-4 py-2 rounded-lg bg-red-50 text-red-600 text-sm">
                {error}
              </div>
            )}

            {tab === 'login' ? (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-sm text-warm-700 mb-1">邮箱</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="请输入邮箱"
                    className="w-full px-4 py-2.5 rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-warm-700 mb-1">密码</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="请输入密码"
                    className="w-full px-4 py-2.5 rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400 text-sm"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 active:bg-warm-800 transition-colors disabled:opacity-50"
                >
                  {loading ? '登录中…' : '登录'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="block text-sm text-warm-700 mb-1">邮箱</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="请输入邮箱"
                    className="w-full px-4 py-2.5 rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-warm-700 mb-1">密码</label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="请输入密码"
                    className="w-full px-4 py-2.5 rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-sm text-warm-700 mb-1">确认密码</label>
                  <input
                    type="password"
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="再次输入密码"
                    className="w-full px-4 py-2.5 rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400 text-sm"
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 rounded-lg bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 active:bg-warm-800 transition-colors disabled:opacity-50"
                >
                  {loading ? '注册中…' : '注册'}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    </main>
  );
}
