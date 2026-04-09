'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Loader2, Sparkles } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { outfits as outfitsApi, clothing as clothingApi } from '@/lib/api';
import { OutfitResponse, CATEGORY_ZH } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

const OCCASION_OPTIONS: { label: string; value: string }[] = [
  { label: '约会', value: 'Date' },
  { label: '工作', value: 'Work' },
  { label: '休闲', value: 'Casual' },
  { label: '运动', value: 'Sport' },
  { label: '聚会', value: 'Formal' },
];

const STYLE_OPTIONS: { label: string; value: string }[] = [
  { label: '简约', value: 'Minimalist' },
  { label: '复古', value: 'Vintage' },
  { label: '街头', value: 'Streetwear' },
  { label: '职业', value: 'Professional' },
];

const SCORE_CONFIG: Record<string, { label: string; className: string }> = {
  A: { label: '完美搭配', className: 'bg-green-100 text-green-700' },
  B: { label: '良好搭配', className: 'bg-yellow-100 text-yellow-700' },
  C: { label: '勉强搭配', className: 'bg-red-100 text-red-600' },
};

export default function GeneratePage() {
  const [occasion, setOccasion] = useState(OCCASION_OPTIONS[0].value);
  const [style, setStyle] = useState(STYLE_OPTIONS[0].value);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tooFewItems, setTooFewItems] = useState(false);
  const [results, setResults] = useState<OutfitResponse[]>([]);
  const [allDone, setAllDone] = useState(false);
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  async function handleGenerate() {
    setError('');
    setTooFewItems(false);
    setAllDone(false);
    setResults([]);
    setLoading(true);
    try {
      // Check wardrobe count first
      const wardrobeRes = await clothingApi.getAll();
      const wardrobeItems = wardrobeRes.data as unknown[];
      if (wardrobeItems.length < 2) {
        setTooFewItems(true);
        return;
      }

      const res = await outfitsApi.generate(occasion, style);
      const data = res.data as OutfitResponse[];
      setResults(Array.isArray(data) ? data : [data]);
    } catch (err) {
      console.error('[generate] API error:', err);
      setError('生成失败，请重试');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(outfit: OutfitResponse) {
    setActionLoading((prev) => ({ ...prev, [outfit.id]: true }));
    try {
      const res = await outfitsApi.save(outfit.id);
      console.log('[save] response:', res.data);
    } catch (err) {
      console.error('[save] error:', err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [outfit.id]: false }));
      removeOutfit(outfit.id);
    }
  }

  async function handleDiscard(outfit: OutfitResponse) {
    setActionLoading((prev) => ({ ...prev, [outfit.id]: true }));
    try {
      await outfitsApi.delete(outfit.id);
    } catch (err) {
      console.error('[discard] error:', err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [outfit.id]: false }));
      removeOutfit(outfit.id);
    }
  }

  function removeOutfit(id: string) {
    setResults((prev) => {
      const next = prev.filter((o) => o.id !== id);
      if (next.length === 0) setAllDone(true);
      return next;
    });
  }

  return (
    <div className="min-h-screen bg-warm-50">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-warm-800">生成搭配</h1>
          <p className="text-sm text-warm-400 mt-0.5">让 AI 为你搭配今日穿搭</p>
        </div>

        {/* Generation form */}
        <div className="bg-white rounded-2xl border border-warm-100 shadow-sm p-5 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex-1">
              <label className="text-xs text-warm-600 block mb-1">场合</label>
              <select
                value={occasion}
                onChange={(e) => setOccasion(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 focus:outline-none focus:ring-2 focus:ring-warm-400"
              >
                {OCCASION_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="text-xs text-warm-600 block mb-1">风格</label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 focus:outline-none focus:ring-2 focus:ring-warm-400"
              >
                {STYLE_OPTIONS.map((s) => (
                  <option key={s.value} value={s.value}>{s.label}</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 disabled:opacity-50 transition-colors whitespace-nowrap"
            >
              {loading ? (
                <><Loader2 size={15} className="animate-spin" /> AI 正在为你搭配...</>
              ) : (
                <><Sparkles size={15} /> ✨ 生成搭配</>
              )}
            </button>
          </div>
        </div>

        {/* Too few items */}
        {tooFewItems && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl px-5 py-4 text-sm text-amber-800">
            请先添加至少 2 件衣物到衣橱。{' '}
            <Link href="/wardrobe" className="underline font-medium hover:text-amber-900">
              去添加衣物
            </Link>
          </div>
        )}

        {/* API error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-5 py-4 text-sm text-red-600">
            {error}
          </div>
        )}

        {/* All outfits handled */}
        {allDone && (
          <div className="text-center py-12">
            <p className="text-warm-500 text-sm mb-4">所有搭配已处理完毕</p>
            <button
              onClick={() => { setAllDone(false); setResults([]); }}
              className="px-5 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 transition-colors"
            >
              生成新的搭配
            </button>
          </div>
        )}

        {/* Results grid */}
        {results.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {results.map((outfit) => {
              const scoreInfo = SCORE_CONFIG[outfit.ai_score] ?? SCORE_CONFIG['C'];
              const busy = actionLoading[outfit.id] ?? false;
              return (
                <div
                  key={outfit.id}
                  className="bg-white rounded-2xl border border-warm-100 shadow-sm overflow-hidden flex flex-col"
                >
                  {/* Card header */}
                  <div className="p-4 border-b border-warm-100">
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="font-semibold text-warm-800 text-sm truncate">{outfit.name}</p>
                        <p className="text-xs text-warm-400 mt-0.5">
                          {new Date(outfit.created_at).toLocaleDateString('zh-CN')}
                        </p>
                      </div>
                      <span className={`shrink-0 text-xs font-medium px-2 py-0.5 rounded-full ${scoreInfo.className}`}>
                        {outfit.ai_score} · {scoreInfo.label}
                      </span>
                    </div>

                    {/* AI explanation */}
                    <p className="text-xs text-warm-600 mt-3 leading-relaxed">{outfit.ai_explanation}</p>

                    {/* Improvement suggestions */}
                    {outfit.improvement_suggestions && (
                      <div className="mt-3 bg-warm-50 border border-warm-200 rounded-lg px-3 py-2">
                        <p className="text-xs font-medium text-warm-700 mb-1">改进建议</p>
                        <p className="text-xs text-warm-600 leading-relaxed">{outfit.improvement_suggestions}</p>
                      </div>
                    )}
                  </div>

                  {/* Clothing thumbnails */}
                  <div className="p-4 flex-1">
                    <p className="text-xs text-warm-500 mb-2">包含单品</p>
                    <div className="grid grid-cols-2 gap-2">
                      {outfit.clothing_items.map((ci) => {
                        const imageUrl = ci.image_url ? API_BASE + ci.image_url : null;
                        return (
                          <div
                            key={ci.id}
                            className="bg-warm-50 rounded-lg border border-warm-100 overflow-hidden"
                          >
                            {imageUrl ? (
                              // eslint-disable-next-line @next/next/no-img-element
                              <img
                                src={imageUrl}
                                alt={ci.sub_category}
                                className="w-full aspect-square object-cover"
                              />
                            ) : (
                              <div
                                className="w-full aspect-square"
                                style={{ backgroundColor: ci.color_code }}
                              />
                            )}
                            <div className="px-1.5 py-1">
                              <p className="text-[10px] font-medium text-warm-800 truncate">{ci.sub_category}</p>
                              <p className="text-[10px] text-warm-400">{CATEGORY_ZH[ci.category] ?? ci.category}</p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Action buttons */}
                  <div className="px-4 pb-4 flex gap-2">
                    <button
                      onClick={() => handleSave(outfit)}
                      disabled={busy}
                      className="flex-1 py-2 rounded-xl bg-green-600 text-white text-xs font-medium hover:bg-green-700 disabled:opacity-50 transition-colors"
                    >
                      {busy ? <Loader2 size={13} className="animate-spin mx-auto" /> : '💾 保存这套'}
                    </button>
                    <button
                      onClick={() => handleDiscard(outfit)}
                      disabled={busy}
                      className="flex-1 py-2 rounded-xl border border-red-200 text-red-500 text-xs font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
                    >
                      {busy ? <Loader2 size={13} className="animate-spin mx-auto" /> : '🗑 丢弃'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
}
