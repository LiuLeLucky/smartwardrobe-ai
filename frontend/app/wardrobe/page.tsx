'use client';

import { useEffect, useState, useRef } from 'react';
import { Plus, Search, X, Loader2 } from 'lucide-react';
import Navbar from '@/components/Navbar';
import ClothingCard from '@/components/ClothingCard';
import { clothing as clothingApi } from '@/lib/api';
import {
  ClothingItem,
  SEASON_LABELS,
  CATEGORY_OPTIONS,
  hexToChineseName,
  COLOR_DOT,
} from '@/lib/types';

const SEASONS = Object.entries(SEASON_LABELS);
const COLOR_FILTERS = Object.keys(COLOR_DOT);

export default function WardrobePage() {
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [seasonFilter, setSeasonFilter] = useState<string>('全部');
  const [colorFilter, setColorFilter] = useState<string>('全部');
  const [search, setSearch] = useState('');

  // Add panel
  const [panelOpen, setPanelOpen] = useState(false);
  const [addCategory, setAddCategory] = useState<string>(CATEGORY_OPTIONS[0]);
  const [addSubCategory, setAddSubCategory] = useState('');
  const [addColorCode, setAddColorCode] = useState('#9c8268');
  const [addMaterial, setAddMaterial] = useState('');
  const [addSeasons, setAddSeasons] = useState<string[]>([]);
  const [addFile, setAddFile] = useState<File | null>(null);
  const [addLoading, setAddLoading] = useState(false);
  const [addAiLoading, setAddAiLoading] = useState(false);
  const [addError, setAddError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  async function fetchItems() {
    setLoading(true);
    setError('');
    try {
      const res = await clothingApi.getAll();
      setItems(res.data as ClothingItem[]);
    } catch {
      setError('加载衣物失败，请刷新重试');
    } finally {
      setLoading(false);
    }
  }

  function toggleAddSeason(s: string) {
    setAddSeasons((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  }

  function resetAddForm() {
    setAddCategory(CATEGORY_OPTIONS[0]);
    setAddSubCategory('');
    setAddColorCode('#9c8268');
    setAddMaterial('');
    setAddSeasons([]);
    setAddFile(null);
    setAddError('');
    if (fileInputRef.current) fileInputRef.current.value = '';
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!addFile && !addSubCategory.trim()) {
      setAddError('请填写衣物名称');
      return;
    }
    setAddError('');
    setAddLoading(true);
    try {
      const res = await clothingApi.create({
        category: addCategory,
        sub_category: addSubCategory.trim() || '待识别',
        color_code: addColorCode,
        material: addMaterial.trim() || '未知',
        season: addSeasons,
      });
      let newItem = res.data as ClothingItem;

      if (addFile) {
        setAddAiLoading(true);
        try {
          const imgRes = await clothingApi.uploadImage(newItem.id, addFile);
          newItem = imgRes.data as ClothingItem;
        } finally {
          setAddAiLoading(false);
        }
      }

      setItems((prev) => [newItem, ...prev]);
      resetAddForm();
      setPanelOpen(false);
    } catch {
      setAddError('添加失败，请重试');
    } finally {
      setAddLoading(false);
    }
  }

  // Client-side filtering
  const filtered = items.filter((item) => {
    if (seasonFilter !== '全部' && !item.season.includes(seasonFilter)) return false;
    if (colorFilter !== '全部' && hexToChineseName(item.color_code) !== colorFilter) return false;
    if (search && !item.sub_category.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="min-h-screen bg-warm-50">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-xl font-semibold text-warm-800">我的衣橱</h1>
            <p className="text-sm text-warm-400 mt-0.5">共 {items.length} 件衣物</p>
          </div>
          <button
            onClick={() => { setPanelOpen((o) => !o); setAddError(''); }}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 transition-colors"
          >
            <Plus size={16} />
            添加衣物
          </button>
        </div>

        {/* Add panel */}
        {panelOpen && (
          <div className="bg-white rounded-2xl border border-warm-100 shadow-sm p-5 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-medium text-warm-800">添加新衣物</h2>
              <button onClick={() => setPanelOpen(false)} className="text-warm-400 hover:text-warm-600">
                <X size={18} />
              </button>
            </div>

            {addError && (
              <div className="mb-3 px-3 py-2 rounded-lg bg-red-50 text-red-600 text-sm">{addError}</div>
            )}

            <form onSubmit={handleAdd} className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-xs text-warm-600 block mb-1">类别</label>
                <select
                  value={addCategory}
                  onChange={(e) => setAddCategory(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 focus:outline-none focus:ring-2 focus:ring-warm-400"
                >
                  {CATEGORY_OPTIONS.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="text-xs text-warm-600 block mb-1">名称</label>
                <input
                  type="text"
                  required={!addFile}
                  placeholder={addFile ? 'AI 将自动识别' : '例如：白色衬衫'}
                  value={addSubCategory}
                  onChange={(e) => setAddSubCategory(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400"
                />
              </div>

              <div>
                <label className="text-xs text-warm-600 block mb-1">颜色</label>
                <div className="flex items-center gap-2">
                  <input
                    type="color"
                    value={addColorCode}
                    onChange={(e) => setAddColorCode(e.target.value)}
                    className="w-10 h-10 rounded-lg border border-warm-200 cursor-pointer"
                  />
                  <span className="text-sm text-warm-500">{addColorCode}</span>
                </div>
              </div>

              <div>
                <label className="text-xs text-warm-600 block mb-1">材质</label>
                <input
                  type="text"
                  placeholder="例如：纯棉"
                  value={addMaterial}
                  onChange={(e) => setAddMaterial(e.target.value)}
                  className="w-full px-3 py-2 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400"
                />
              </div>

              <div>
                <label className="text-xs text-warm-600 block mb-1">季节</label>
                <div className="flex gap-2 flex-wrap">
                  {SEASONS.map(([key, label]) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => toggleAddSeason(key)}
                      className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                        addSeasons.includes(key)
                          ? 'bg-warm-600 text-white border-warm-600'
                          : 'border-warm-200 text-warm-600 hover:bg-warm-100'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-xs text-warm-600 block mb-1">照片（可选）</label>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setAddFile(e.target.files?.[0] ?? null)}
                  className="w-full text-sm text-warm-600 file:mr-3 file:py-1 file:px-3 file:rounded-lg file:border-0 file:bg-warm-100 file:text-warm-600 hover:file:bg-warm-200"
                />
              </div>

              <div className="sm:col-span-2 flex justify-end">
                <button
                  type="submit"
                  disabled={addLoading || addAiLoading}
                  className="flex items-center gap-2 px-6 py-2 rounded-xl bg-warm-600 text-white text-sm font-medium hover:bg-warm-700 disabled:opacity-50 transition-colors"
                >
                  {addAiLoading ? (
                    <><Loader2 size={14} className="animate-spin" /> AI 正在识别...</>
                  ) : addLoading ? (
                    <><Loader2 size={14} className="animate-spin" /> 添加中…</>
                  ) : '确认添加'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filter bar */}
        <div className="bg-white rounded-2xl border border-warm-100 shadow-sm p-4 mb-6 space-y-3">
          {/* Season filter */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-warm-500 shrink-0">季节</span>
            {['全部', ...Object.keys(SEASON_LABELS)].map((key) => {
              const label = key === '全部' ? '全部' : SEASON_LABELS[key];
              return (
                <button
                  key={key}
                  onClick={() => setSeasonFilter(key)}
                  className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                    seasonFilter === key
                      ? 'bg-warm-600 text-white border-warm-600'
                      : 'border-warm-200 text-warm-600 hover:bg-warm-100'
                  }`}
                >
                  {label}
                </button>
              );
            })}
          </div>

          {/* Color filter */}
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-warm-500 shrink-0">颜色</span>
            <button
              onClick={() => setColorFilter('全部')}
              className={`px-3 py-1 rounded-full text-xs border transition-colors ${
                colorFilter === '全部'
                  ? 'bg-warm-600 text-white border-warm-600'
                  : 'border-warm-200 text-warm-600 hover:bg-warm-100'
              }`}
            >
              全部
            </button>
            {COLOR_FILTERS.map((name) => (
              <button
                key={name}
                onClick={() => setColorFilter(name)}
                className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs border transition-colors ${
                  colorFilter === name
                    ? 'bg-warm-600 text-white border-warm-600'
                    : 'border-warm-200 text-warm-600 hover:bg-warm-100'
                }`}
              >
                <span
                  className="w-3 h-3 rounded-full border border-black/10"
                  style={{ backgroundColor: COLOR_DOT[name] }}
                />
                {name}
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative max-w-xs">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-warm-300" />
            <input
              type="text"
              placeholder="搜索衣物名称…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-sm rounded-lg border border-warm-200 bg-warm-50 text-warm-800 placeholder-warm-300 focus:outline-none focus:ring-2 focus:ring-warm-400"
            />
          </div>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <Loader2 size={28} className="animate-spin text-warm-400" />
          </div>
        ) : error ? (
          <div className="text-center py-20 text-red-500 text-sm">{error}</div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20 text-warm-400 text-sm">
            {items.length === 0 ? '衣橱还是空的，添加你的第一件衣物吧 👗' : '没有符合条件的衣物'}
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((item) => (
              <ClothingCard
                key={item.id}
                item={item}
                onUpdated={(updated) =>
                  setItems((prev) => prev.map((i) => (i.id === updated.id ? updated : i)))
                }
                onDeleted={(id) => setItems((prev) => prev.filter((i) => i.id !== id))}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
