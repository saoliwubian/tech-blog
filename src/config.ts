import type {
	ExpressiveCodeConfig,
	LicenseConfig,
	NavBarConfig,
	ProfileConfig,
	SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
	title: "TechPulse",
	subtitle: "探索科技前沿 · 洞察数字未来",
	lang: "zh_CN",
	themeColor: {
		hue: 200, // 科技蓝，从0到360。红色:0, 青色:200, 蓝紫:250, 粉色:345
		fixed: false,
	},
	banner: {
		enable: true,
		src: "assets/images/demo-banner.png",
		position: "center",
		credit: {
			enable: false,
			text: "",
			url: "",
		},
	},
	toc: {
		enable: true,
		depth: 2,
	},
	favicon: [
		// Leave this array empty to use the default favicon
	],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		LinkPreset.About,
		{
			name: "AI 日报",
			url: "/ai-daily/",
		},
		{
			name: "GitHub",
			url: "https://github.com/saoliwubian/tech-blog",
			external: true,
		},
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "assets/images/demo-avatar.png",
	name: "TechPulse",
	bio: "专注于人工智能、Web 开发、云计算与开源技术的深度科技博客",
	links: [
		{
			name: "GitHub",
			icon: "fa6-brands:github",
			url: "https://github.com/saoliwubian/tech-blog",
		},
		{
			name: "Twitter",
			icon: "fa6-brands:twitter",
			url: "https://twitter.com",
		},
		{
			name: "RSS",
			icon: "fa6-solid:rss",
			url: "/rss.xml",
		},
	],
};

export const licenseConfig: LicenseConfig = {
	enable: true,
	name: "CC BY-NC-SA 4.0",
	url: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
};

export const expressiveCodeConfig: ExpressiveCodeConfig = {
	theme: "github-dark",
};
