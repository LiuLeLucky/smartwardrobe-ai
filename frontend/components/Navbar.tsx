'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Menu, X } from 'lucide-react';
import { useAuthStore } from '@/lib/store';

const NAV_LINKS = [
  { href: '/wardrobe',      label: '我的衣橱' },
  { href: '/generate',      label: '生成搭配' },
  { href: '/create-outfit', label: '创建搭配' },
  { href: '/outfits',       label: '我的穿搭' },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [menuOpen, setMenuOpen] = useState(false);

  function handleLogout() {
    logout();
    router.push('/login');
  }

  return (
    <nav className="bg-white border-b border-warm-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link href="/wardrobe" className="flex items-center gap-2 text-warm-800 font-semibold text-base shrink-0">
          <span className="text-xl">👗</span>
          <span>智能衣橱 AI</span>
        </Link>

        {/* Desktop nav links */}
        <div className="hidden md:flex items-center gap-1">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                pathname.startsWith(href)
                  ? 'bg-warm-100 text-warm-600 font-medium'
                  : 'text-warm-500 hover:text-warm-700 hover:bg-warm-50'
              }`}
            >
              {label}
            </Link>
          ))}
        </div>

        {/* Desktop right: user + logout */}
        <div className="hidden md:flex items-center gap-3">
          {user?.email && (
            <span className="text-xs text-warm-400 max-w-[160px] truncate">{user.email}</span>
          )}
          <button
            onClick={handleLogout}
            className="text-sm px-3 py-1.5 rounded-lg border border-warm-200 text-warm-600 hover:bg-warm-50 transition-colors"
          >
            退出登录
          </button>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden p-1.5 text-warm-600"
          onClick={() => setMenuOpen((o) => !o)}
          aria-label="菜单"
        >
          {menuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div className="md:hidden border-t border-warm-100 bg-white px-4 py-3 space-y-1">
          {NAV_LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              onClick={() => setMenuOpen(false)}
              className={`block px-3 py-2 rounded-lg text-sm ${
                pathname.startsWith(href)
                  ? 'bg-warm-100 text-warm-600 font-medium'
                  : 'text-warm-600 hover:bg-warm-50'
              }`}
            >
              {label}
            </Link>
          ))}
          <div className="pt-2 border-t border-warm-100 flex items-center justify-between">
            {user?.email && (
              <span className="text-xs text-warm-400 truncate max-w-[180px]">{user.email}</span>
            )}
            <button
              onClick={() => { setMenuOpen(false); handleLogout(); }}
              className="text-sm px-3 py-1.5 rounded-lg border border-warm-200 text-warm-600 hover:bg-warm-50"
            >
              退出登录
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}
