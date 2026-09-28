import type { ImageMetadata } from 'astro';
import defaultAvatar from '../assets/profile.jpg';

/**
 * Allowed social entry keys in profile configuration.
 */
export type ProfileSocialKey = 'github' | 'email';

/**
 * One social link item rendered on `/about`.
 */
export interface ProfileSocialLink {
  key: ProfileSocialKey;
  label: string;
  url: string;
}

/**
 * Personal profile settings used by About page and article author schema.
 */
export interface ProfileConfig {
  /**
   * Optional avatar URL for About page and structured data.
   */
  avatar?: string | ImageMetadata;
  /**
   * Display name used across the site.
   */
  name: string;
  /**
   * Short headline/title shown on About page.
   */
  title: string;
  /**
   * Short bio text shown on About page and in schema.
   */
  bio: string;
  /**
   * Optional location text.
   */
  location?: string;
  /**
   * Optional contact email.
   */
  email?: string;
  /**
   * Personal GitHub profile URL (separate from repo URL).
   */
  githubProfileUrl: string;
  /**
   * Social links displayed in About page social row.
   */
  socials: ProfileSocialLink[];
}

export const profileConfig: ProfileConfig = {
  avatar: defaultAvatar,
  name: 'Alexander Ma',
  title: 'CUPL法学在读',
  bio: '我崇拜着如肖潇、香农、吴恩达、姚顺雨的一表英才，浸润在是海德格尔、福柯、桑塔格、马克思·韦伯、阿多诺或黑塞的思想中，还深切热爱李斯特和肖邦，但也是终究谁也没成为的失意之人。',
  location: '北京/石家庄',
  email: 'matianlaialex@sina.com',
  githubProfileUrl: 'https://github.com/TLHorse',
  socials: [
    { key: 'github', label: 'GitHub', url: 'https://github.com/TLHorse' },
    { key: 'email', label: 'Email', url: 'mailto:matianlaialex@sina.com' }
  ],
};
