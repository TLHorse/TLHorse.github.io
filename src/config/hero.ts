import defaultBackground from '../assets/thumb.jpg';

/**
 * Hero copy and background settings for one page.
 */
export interface HeroSectionConfig {
  /**
   * Main hero headline text.
   */
  text: string;
  /**
   * Optional hero subtitle text.
   */
  subtitle?: string;
  /**
   * Hero background image URL.
   */
  backgroundImage: string;
}

/**
 * Centralized hero configuration for all top-level pages and post fallback.
 */
export interface HeroConfig {
  home: HeroSectionConfig;
  blog: HeroSectionConfig;
  tags: HeroSectionConfig;
  about: HeroSectionConfig;
  /**
   * Default hero image shared by all article pages.
   */
  postDefaultBackground: string;
}

export const heroConfig: HeroConfig = {
  home: {
    text: '命运将我推向何处，我便一往无前。',
    subtitle: 'Where fate doth drive me, thither I press onward without fear.',
    backgroundImage: defaultBackground.src,
  },
  blog: {
    text: '文存',
    subtitle: '浏览写作存档，所有文章汇集于此。',
    backgroundImage: defaultBackground.src,
  },
  tags: {
    text: '索引',
    subtitle: '浏览话题分类和标签，发现相关内容。',
    backgroundImage: defaultBackground.src,
  },
  about: {
    text: '自述',
    subtitle: '个人介绍、联系方式和社交链接。',
    backgroundImage: defaultBackground.src,
  },
  postDefaultBackground: defaultBackground.src,
};
