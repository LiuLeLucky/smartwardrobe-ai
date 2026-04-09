'use client';

import { useEffect, useState } from 'react';
import { Check, Loader2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { clothing as clothingApi, outfits as outfitsApi } from '@/lib/api';
import { ClothingItem, CATEGORY_ZH } from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';

const OCCASION_OPTIONS: { label: string; value: string }[] = [
  { label: '约会', value: 'Date' },
  { label: '工作', value: 'Work' },
  { label: '休闲', value: 'Casual' },
  { label: '运动', value: 'Sport' },
  { label: '聚会', value: 'Party' },
];

export default function CreateOutfitPage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loadingItems, setLoadingItems] = useState(true);
  const [loadError, setLoadError] = useState('');

  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [occasion, setOccasion] = useState(OCCASION_OPTIONS[0].value);
  const [outfitName, setOutfitName] = useState('');

  const [saving, setSaving] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [saveError, setSaveError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    clothingApi.getAll()
      .then((res) => setItems(res.data as ClothingItem[]))
      .catch(() => setLoadError('加载衣物失败，请刷新重试'))
      .finally(() => setLoadingItems(false));
  }, []);

  function toggleItem(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    setValidationError('');
    setSuccess(false);
  }

  async function handleCreate() {
    if (selected.size < 2) {
      setValidationError('请至少选择 2 件单品');
      return;
    }
    setValidationError('');
    setSaveError('');
    setSuccess(false);
    setSaving(true);

    const name =
      outfitName.trim() ||
      `我的搭配 - ${new Date().toLocaleDateString('zh-CN')}`;

    try {
      await outfitsApi.create({
        name,
        occasion,
        clothing_item_ids: Array.from(selected),
      });
      setSuccess(true);
      setSelected(new Set());
      setOutfitName('');
    } catch {
      setSaveError('创建失败，请重试');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-warm-50">
      <Navbar />

      <main className="max-w-5xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-warm-800">创建搭配</h1>
          <p className="text-sm text-warm-400 mt-0.5">手动挑选单品，创建你的专属搭配</p>
        </div>

        {/* Load error */}
        {loadError && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 text-sm text-red-600 mb-6">
            {loadError}
          </div>
        )}

        {/* Selection counter */}
        {!loadingItems && items.length > 0 && (
          <p className="text-sm text-warm-600 mb-3">
            已选择{' '}
            <span className="font-semibold text-warm-800">{selected.size}</span>{' '}
            件单品
          </p>
        )}

        {/* Clothing grid */}
        {loadingItems ? (
          <div className="flex justify-center py-20">
            <Loader2 size={28} className="animate-spin text-warm-400" />
          </div>
        ) : items.length === 0 && !loadError ? (
          <div className="text-center py-20 text-warm-400 text-sm">
            衣橱还是空的，请先前往衣橱添加衣物
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {items.map((item) => {
              const isSelected = selected.has(item.id);
              const imageUrl = item.image_url ? API_BASE + item.image_url : null;
              return (
                <div
                  key={item.id}
                  onClick={() => toggleItem(item.id)}
                  className={`relative bg-white rounded-xl border-2 overflow-hidden shadow-sm cursor-pointer transition-all select-none ${
                    isSelected
                      ? 'border-warm-600 shadow-md'
                      : 'border-warm-100 hover:border-warm-300 hover:shadow-md'
                  }`}
                >
                  {/* Checkbox overlay */}
                  <div
                    className={`absolute top-2 right-2 z-10 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                      isSelected
                        ? 'bg-warm-600 border-warm-600'
                        : 'bg-white/80 border-warm-300'
                    }`}
                  >
                    {isSelected && <Check size={11} strokeWidth={3} className="text-white" />}
                  </div>

                  {/* Image or color block */}
                  {imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={imageUrl}
                      alt={item.sub_category}
                      className="w-full aspect-[4/3] object-cover"
                    />
                  ) : (
                    <div
                      className="w-full aspect-[4/3]"
                      style={{ backgroundColor: item.color_code }}
                    />
                  )}

                  {/* Item info */}
                  <div className="p-3">
                    <p className="font-medium text-warm-800 text-sm truncate">{item.sub_category}</p>
                    <p className="text-xs text-warm-400 mt-0.5">
                      {CATEGORY_ZH[item.category] ?? item.category}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Outfit details form */}
        {!loadingItems && items.length > 0 && (
          <div className="bg-white rounded-2xl border border-warm-100 shadow-sm p-5">
            <h2 className="text-base font-medium text-warm-800 mb-4">搭配详情</h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
              <div>
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

              <div>
                <label className="text-xs text-warm-600 block mb-1">搭配名称（可选）</label>
                <input
                  type="text"
                  value={outfitName}
                  onChange={(e) => setOutfitName(e.target.value)}
                  placeholder="留空将自动生成名称"
                  className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400"
                />
              </div>
            </div>

            {/* Validation / save errors */}
            {validationError && (
              <p className="text-sm text-red-500 mb-3">{validationError}</p>
            )}
            {saveError && (
              <p className="text-sm text-red-500 mb-3">{saveError}</p>
            )}
            {success && (
              <p className="text-sm text-green-600 mb-3">搭配创建成功！</p>
            )}

            <button
              onClick={handleCreate}
              disabled={saving}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 disabled:opacity-50 transition-colors"
            >
              {saving ? (
                <><Loader2 size={15} className="animate-spin" /> 创建中…</>
              ) : (
                '✨ 创建搭配'
              )}
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
