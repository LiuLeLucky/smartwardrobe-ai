export interface OutfitResponse {
  id: string;
  name: string;
  occasion: string;
  ai_explanation: string;
  ai_score: string;
  improvement_suggestions: string;
  source: string;
  is_saved: boolean;
  created_at: string;
  clothing_items: ClothingItem[];
}

export interface ClothingItem {
  id: string;
  user_id: string;
  category: string;
  sub_category: string;
  color_code: string;
  material: string;
  season: string[];
  image_url: string | null;
  vector_id: string | null;
  raw_ai_metadata: Record<string, unknown> | null;
  created_at: string;
}

// Season values stored in backend
export const SEASON_LABELS: Record<string, string> = {
  spring: '春',
  summer: '夏',
  autumn: '秋',
  winter: '冬',
};

export const CATEGORY_OPTIONS = ['上衣', '裤子', '鞋子', '外套', '配件'] as const;

export const CATEGORY_ZH: Record<string, string> = {
  Top: '上衣',
  Bottom: '裤子',
  Shoes: '鞋子',
  Outerwear: '外套',
  Accessory: '配件',
};

// Convert hex color code to approximate Chinese color name
export function hexToChineseName(hex: string): string {
  if (!hex || hex.length < 7) return '自定义颜色';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  const rn = r / 255, gn = g / 255, bn = b / 255;
  const max = Math.max(rn, gn, bn), min = Math.min(rn, gn, bn);
  const l = (max + min) / 2;
  const d = max - min;
  const s = d === 0 ? 0 : d / (1 - Math.abs(2 * l - 1));

  if (s < 0.15) {
    if (l > 0.82) return '白色';
    if (l < 0.20) return '黑色';
    return '灰色';
  }

  let h = 0;
  if (d !== 0) {
    if (max === rn) h = ((gn - bn) / d + 6) % 6;
    else if (max === gn) h = (bn - rn) / d + 2;
    else h = (rn - gn) / d + 4;
    h *= 60;
  }

  if (h < 20 || h >= 345) return '红色';
  if (h < 55) return l < 0.45 ? '棕色' : '其他'; // orange/brown/yellow
  if (h < 165) return '绿色';
  if (h < 265) return '蓝色';
  return '其他'; // purple
}

// Map Chinese color name → a representative display hex for the color dot
export const COLOR_DOT: Record<string, string> = {
  '白色': '#FFFFFF',
  '黑色': '#1a1a1a',
  '灰色': '#808080',
  '蓝色': '#3B7DD8',
  '红色': '#D63030',
  '绿色': '#2E8B40',
  '棕色': '#7c5c3a',
  '其他': '#b09880',
};
