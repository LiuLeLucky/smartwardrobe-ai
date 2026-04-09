'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Loader2, Trash2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { outfits as outfitsApi } from '@/lib/api';
import { OutfitResponse, CATEGORY_ZH } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

const OCCASION_ZH: Record<string, string> = {
  Date: '约会',
  Work: '工作',
  Casual: '休闲',
  Sport: '运动',
  Formal: '聚会',
  Party: '聚会',
};

const SCORE_CONFIG: Record<string, { label: string; className: string }> = {
  A: { label: '完美搭配', className: 'bg-green-100 text-green-700' },
  B: { label: '良好搭配', className: 'bg-yellow-100 text-yellow-700' },
  C: { label: '勉强搭配', className: 'bg-gray-100 text-gray-500' },
};

type Tab = 'ai' | 'manual';

export default function OutfitsPage() {
  const [allOutfits, setAllOutfits] = useState<OutfitResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [tab, setTab] = useState<Tab>('ai');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [deletedMsg, setDeletedMsg] = useState(false);

  useEffect(() => {
    outfitsApi.getAll()
      .then((res) => {
        const data = (res.data as OutfitResponse[])
          .filter((o) => o.is_saved)
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setAllOutfits(data);
      })
      .catch(() => setLoadError('加载搭配失败，请刷新重试'))
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(outfit: OutfitResponse) {
    if (!window.confirm('确认删除这套搭配？')) return;
    setDeletingId(outfit.id);
    try {
      await outfitsApi.delete(outfit.id);
      setAllOutfits((prev) => prev.filter((o) => o.id !== outfit.id));
      setDeletedMsg(true);
      setTimeout(() => setDeletedMsg(false), 3000);
    } finally {
      setDeletingId(null);
    }
  }

  const aiOutfits = allOutfits.filter((o) => o.source === 'ai');
  const manualOutfits = allOutfits.filter((o) => o.source === 'manual');
  const displayed = tab === 'ai' ? aiOutfits : manualOutfits;

  return (
    <div className="min-h-screen bg-warm-50">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-warm-800">我的穿搭</h1>
          <p className="text-sm text-warm-400 mt-0.5">你保存的所有搭配</p>
        </div>

        {/* Deleted toast */}
        {deletedMsg && (
          <div className="bg-green-50 border border-green-200 rounded-xl px-4 py-3 text-sm text-green-700 mb-4">
            搭配已删除
          </div>
        )}

        {/* Load error */}
        {loadError && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600 mb-4">
            {loadError}
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {(
            [
              { key: 'ai' as Tab, label: 'AI 搭配', count: aiOutfits.length },
              { key: 'manual' as Tab, label: '我的搭配', count: manualOutfits.length },
            ] as const
          ).map(({ key, label, count }) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                tab === key
                  ? 'bg-warm-600 text-white'
                  : 'bg-white border border-warm-200 text-warm-600 hover:bg-warm-50'
              }`}
            >
              {label}
              {!loading && (
                <span
                  className={`ml-1.5 text-xs px-1.5 py-0.5 rounded-full ${
                    tab === key ? 'bg-white/20 text-white' : 'bg-warm-100 text-warm-500'
                  }`}
                >
                  {count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 size={28} className="animate-spin text-warm-400" />
          </div>
        ) : displayed.length === 0 ? (
          <div className="text-center py-20 text-warm-400 text-sm space-y-3">
            {tab === 'ai' ? (
              <>
                <p>还没有保存的 AI 搭配，去生成一套吧！</p>
                <Link
                  href="/generate"
                  className="inline-block px-4 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 transition-colors"
                >
                  去生成搭配
                </Link>
              </>
            ) : (
              <>
                <p>还没有手动创建的搭配，去创建一套吧！</p>
                <Link
                  href="/create-outfit"
                  className="inline-block px-4 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 transition-colors"
                >
                  去创建搭配
                </Link>
              </>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {displayed.map((outfit) => {
              const scoreInfo = outfit.ai_score ? SCORE_CONFIG[outfit.ai_score] : null;
              const occasionZh = outfit.occasion ? (OCCASION_ZH[outfit.occasion] ?? outfit.occasion) : null;
              const deleting = deletingId === outfit.id;

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
                          {new Date(outfit.created_at).toLocaleDateString('zh-CN', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </p>
                      </div>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {occasionZh && (
                          <span className="text-xs px-2 py-0.5 rounded-full bg-warm-100 text-warm-600">
                            {occasionZh}
                          </span>
                        )}
                        {scoreInfo && (
                          <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${scoreInfo.className}`}>
                            {outfit.ai_score} · {scoreInfo.label}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* AI explanation */}
                    {outfit.ai_explanation && (
                      <p className="text-xs text-warm-600 mt-3 leading-relaxed">{outfit.ai_explanation}</p>
                    )}

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
                    <div className="grid grid-cols-3 gap-2">
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

                  {/* Delete button */}
                  <div className="px-4 pb-4">
                    <button
                      onClick={() => handleDelete(outfit)}
                      disabled={deleting}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-red-200 text-red-500 text-xs font-medium hover:bg-red-50 disabled:opacity-50 transition-colors"
                    >
                      {deleting ? (
                        <Loader2 size={12} className="animate-spin" />
                      ) : (
                        <Trash2 size={12} />
                      )}
                      {deleting ? '删除中…' : '🗑 删除'}
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
