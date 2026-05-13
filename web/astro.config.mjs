// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	devToolbar: {
		enabled: false,
	},
	vite: {
		server: {
			allowedHosts: ['.ts.net', '.local', '100.76.38.110', 'localhost'],
		},
	},
	integrations: [
		starlight({
			title: "Chemist's AI Workflow",
			description: '化学者のための AI エージェント活用法 — 研究室そのものを多部署化する実践メソッド',
			defaultLocale: 'root',
			locales: {
				root: { label: '日本語', lang: 'ja' },
			},
			social: [],
			sidebar: [
				{
					label: 'はじめに',
					items: [
						{ label: 'プロジェクト概要', slug: 'about' },
						{ label: '誰のためのものか', slug: 'audience' },
						{ label: '対応ツール一覧', slug: 'tools' },
						{ label: '配布プラグイン（caw）', slug: 'plugin' },
						{ label: 'ロードマップ', slug: 'roadmap' },
					],
				},
				{
					label: '核：CLI 中立メソッド',
					items: [
						{ label: 'core/ 概要', slug: 'core' },
					],
				},
				{
					label: 'Tier 1: Claude Code（premium）',
					items: [
						{ label: '概要', slug: 'claude-code' },
						{ label: '環境構築', slug: 'claude-code/setup' },
						{ label: '設定の階層と基礎', slug: 'claude-code/basics' },
						{ label: 'Skills', slug: 'claude-code/skills' },
						{ label: 'Hooks', slug: 'claude-code/hooks' },
						{ label: 'Sub-agents', slug: 'claude-code/subagents' },
						{ label: 'MCP サーバー連携', slug: 'claude-code/mcp' },
						{ label: '.company/ 部署テンプレート', slug: 'claude-code/company-template' },
						{ label: '応用：化学研究での実例', slug: 'claude-code/application' },
						{ label: 'Claude + Codex 二段レビュー', slug: 'claude-code/two-stage-review' },
					],
				},
				{
					label: 'Tier 2: Codex CLI（次点）',
					items: [
						{ label: 'codex-cli/ 概要', slug: 'codex-cli' },
					],
				},
				{
					label: 'Tier 3: Gemini CLI（OSS）',
					items: [
						{ label: 'gemini-cli/ 概要', slug: 'gemini-cli' },
					],
				},
				{
					label: 'Tier 4: Web 版（最小）',
					items: [
						{ label: 'chatgpt-web/ 概要', slug: 'chatgpt-web' },
					],
				},
			],
		}),
	],
});
