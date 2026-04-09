'use client';

import { useState } from 'react';
import { Pencil, Trash2, Check, X } from 'lucide-react';
import { clothing } from '@/lib/api';
import {
  ClothingItem,
  SEASON_LABELS,
  CATEGORY_ZH,
  hexToChineseName,
} from '@/lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? '';


const CATEGORY_EN_OPTIONS = [
  { value: 'Top', label: '上衣' },
  { value: 'Bottom', label: '裤子' },
  { value: 'Shoes', label: '鞋子' },
  { value: 'Outerwear', label: '外套' },
  { value: 'Accessory', label: '配件' },
];

interface Props {
  item: ClothingItem;
  onUpdated: (item: ClothingItem) => void;
  onDeleted: (id: string) => void;
}

export default function ClothingCard({ item, onUpdated, onDeleted }: Props) {
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [saving, setSaving] = useState(false);

  const [editCategory, setEditCategory] = useState(item.category);
  const [editSubCategory, setEditSubCategory] = useState(item.sub_category);
  const [editColorCode, setEditColorCode] = useState(item.color_code);
  const [editMaterial, setEditMaterial] = useState(item.material);
  const [editSeason, setEditSeason] = useState<string[]>(item.season);

  function toggleSeason(s: string) {
    setEditSeason((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  }

  function openEdit() {
    setEditCategory(item.category);
    setEditSubCategory(item.sub_category);
    setEditColorCode(item.color_code);
    setEditMaterial(item.material);
    setEditSeason([...item.season]);
    setEditing(true);
  }

  async function handleSave() {
    setSaving(true);
    try {
      const res = await clothing.update(item.id, {
        category: editCategory,
        sub_category: editSubCategory,
        color_code: editColorCode,
        material: editMaterial,
        season: editSeason,
      });
      onUpdated(res.data as ClothingItem);
      setEditing(false);
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    setDeleting(true);
    try {
      await clothing.delete(item.id);
      onDeleted(item.id);
    } finally {
      setDeleting(false);
    }
  }

  const colorName = hexToChineseName(item.color_code);
  const imageUrl = item.image_url ? API_BASE + item.image_url : null;

  return (
    <div className="bg-white rounded-xl border border-warm-100 overflow-hidden shadow-sm hover:shadow-md transition-shadow self-start">
      {/* Image / color placeholder */}
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
          style={{ backgroundColor: editing ? editColorCode : item.color_code }}
        />
      )}

      {editing ? (
        /* Edit mode: card body replaced in-place with edit form */
        <div className="p-3 space-y-2">
          <div>
            <label className="text-xs text-warm-600 block mb-0.5">类别</label>
            <select
              value={editCategory}
              onChange={(e) => setEditCategory(e.target.value)}
              className="w-full px-2 py-1.5 text-xs rounded-lg border border-warm-200 bg-white text-warm-800 focus:outline-none focus:ring-1 focus:ring-warm-400"
            >
              {CATEGORY_EN_OPTIONS.map((c) => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs text-warm-600 block mb-0.5">名称</label>
            <input
              type="text"
              value={editSubCategory}
              onChange={(e) => setEditSubCategory(e.target.value)}
              className="w-full px-2 py-1.5 text-xs rounded-lg border border-warm-200 bg-white text-warm-800 focus:outline-none focus:ring-1 focus:ring-warm-400"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="text-xs text-warm-600 shrink-0">颜色</label>
            <input
              type="color"
              value={editColorCode}
              onChange={(e) => setEditColorCode(e.target.value)}
              className="w-8 h-8 rounded border border-warm-200 cursor-pointer"
            />
            <span className="text-xs text-warm-400">{editColorCode}</span>
          </div>
          <div>
            <label className="text-xs text-warm-600 block mb-0.5">材质</label>
            <input
              type="text"
              value={editMaterial}
              onChange={(e) => setEditMaterial(e.target.value)}
              className="w-full px-2 py-1.5 text-xs rounded-lg border border-warm-200 bg-white text-warm-800 focus:outline-none focus:ring-1 focus:ring-warm-400"
            />
          </div>
          <div>
            <label className="text-xs text-warm-600 block mb-1">季节</label>
            <div className="flex gap-1.5 flex-wrap">
              {Object.entries(SEASON_LABELS).map(([key, label]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => toggleSeason(key)}
                  className={`px-2 py-0.5 rounded-full text-xs border transition-colors ${
                    editSeason.includes(key)
                      ? 'bg-warm-600 text-white border-warm-600'
                      : 'border-warm-200 text-warm-600 hover:bg-warm-100'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg bg-warm-600 text-white hover:bg-warm-700 disabled:opacity-50 transition-colors"
            >
              <Check size={12} /> {saving ? '保存中…' : '保存'}
            </button>
            <button
              onClick={() => setEditing(false)}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg border border-warm-200 text-warm-600 hover:bg-warm-100 transition-colors"
            >
              <X size={12} /> 取消
            </button>
          </div>
        </div>
      ) : (
        /* View mode: normal card display */
        <div className="p-3">
          <p className="font-semibold text-warm-800 text-sm truncate">{item.sub_category}</p>
          <p className="text-xs text-warm-400 mt-0.5">{CATEGORY_ZH[item.category] ?? item.category}</p>

          <div className="flex items-center gap-1.5 mt-2">
            <span
              className="w-3.5 h-3.5 rounded-full border border-warm-200 shrink-0"
              style={{ backgroundColor: item.color_code }}
            />
            <span className="text-xs text-warm-600">{colorName}</span>
          </div>

          {item.material && (
            <p className="text-xs text-warm-400 mt-1">{item.material}</p>
          )}

          {item.season.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {item.season.map((s) => (
                <span
                  key={s}
                  className="text-[10px] px-1.5 py-0.5 rounded-full bg-warm-100 text-warm-600"
                >
                  {SEASON_LABELS[s] ?? s}
                </span>
              ))}
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-2 mt-3">
            <button
              onClick={openEdit}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg border border-warm-200 text-warm-600 hover:bg-warm-50 transition-colors"
            >
              <Pencil size={12} /> 编辑
            </button>
            <button
              onClick={handleDelete}
              disabled={deleting}
              className="flex-1 flex items-center justify-center gap-1 py-1.5 text-xs rounded-lg border border-red-200 text-red-500 hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              <Trash2 size={12} /> {deleting ? '删除中…' : '删除'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
