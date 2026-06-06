import type {
	ExpressiveCodeConfig,
	LicenseConfig,
	NavBarConfig,
	ProfileConfig,
	SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
	title: "TechPulse 科技脉搏",
	subtitle: "探索前沿技术，洞察数字未来",
	lang: "zh_CN",
	themeColor: {
		hue: 210, // 科技蓝
		fixed: false,
	},
	banner: {
		enable: true,
		src: "assets/images/tech-banner.svg",
		position: "center",
		credit: {
			enable: false,
			text: "",
			url: "",
		},
	},
	toc: {
		enable: true,
		depth: 3,
	},
	favicon: [],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		LinkPreset.About,
		{
			name: "GitHub",
			url: "https://github.com/saoliwubian/tech-blog",
			external: true,
		},
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "assets/images/tech-avatar.svg",
	name: "TechPulse",
	bio: "探索人工智能、云计算、前端开发与系统编程的前沿技术。用代码改变世界，用技术创造未来。",
	links: [
		{
			name: "GitHub",
			icon: "fa6-brands:github",
			url: "https://github.com/saoliwubian",
		},
		{
			name: "X",
			icon: "fa6-brands:x-twitter",
			url: "https://x.com",
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
