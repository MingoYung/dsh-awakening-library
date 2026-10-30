# 鲸启动画库 · Awakening Library

给 [鲸启 · dsh-awakening](https://github.com/MingoYung/dsh-awakening) 提供可浏览、可下载的开机动画目录，也给创作者提供投稿入口。它是社区作品库，不代表 DeepSeek 或 DSH 官方发布、合作或背书。

在鲸启 **[0.7.0](https://github.com/MingoYung/dsh-awakening/releases/tag/v0.7.0)** 的“动画库”页内浏览封面、分类、搜索和作品详情，首次进入时更新目录，也可手动刷新；“下载并使用”可以一步下载并选用。0.7.0 随包带有下列三部主题，离线即可选择；与目录中相同作品按 ID/摘要关联，避免重复下载。“创作与投稿”在页内展示说明及模板，实际投稿仍需通过社区审核。此前的 0.6.1 与 0.6.0 版本仍可读取兼容目录，第三方视频按原有播放器能力显示。

下载后从本地播放，正常开机不请求动画库。首批作品发布在固定版本 [starter-v1.0.0](https://github.com/MingoYung/dsh-awakening-library/releases/tag/starter-v1.0.0)：

| 作品 | 画面与声音 | 来源、工程与媒体许可 |
| --- | --- | --- |
| DeepSeek · 鲸启 | 鲸鱼标志、文字聚合与流光汇成人物；22秒有声 | [作品与源码快照](works/deepseek-awakening/) · [署名](works/deepseek-awakening/CREDITS.md) · [许可](works/deepseek-awakening/LICENSE.md) |
| Codex · 构想成形 | 铂白、薄荷色与银发编程伙伴；22秒有声 | [作品与工程](works/codex-awakening/) · [署名](works/codex-awakening/CREDITS.md) · [许可](works/codex-awakening/LICENSE.md) |
| Claude Code · 光标唤醒 | Clawd、终端光标与柔性光丝；22秒有声 | [作品与工程](works/claude-code-awakening/) · [署名](works/claude-code-awakening/CREDITS.md) · [许可](works/claude-code-awakening/LICENSE.md) |

三部角色影像、合成欢迎语和原创音效均为本项目这轮重新制作，不再拼接旧版第三方角色欢迎视频。角色是原创同人形象，品牌标志单独保留权利。历史 `mingoyung.awakening` 内置条目继续保留旧版来源与 MIT 通知，供旧版插件兼容，不能把其旧影片署名套到新三部作品上。

也可以从插件设置中直接导入自己的 MP4 或 WebM。私人导入文件留在使用者的本机，不会自动上传到 GitHub 或本库。社区目录中的普通视频与内置鲸启的程序构图不同：普通视频按所选“填满窗口 / 完整画面”显示，不会自动把人物与字幕重新排版。

## 给创作者

欢迎提供原创作品或拥有充分分发授权的作品。阅读 [投稿说明](CONTRIBUTING.md)，复制 [条目模板](template/animation.json)，然后只新增一个 `entries/<作品ID>.json` 提交 Pull Request。

- 视频放在作者自己的 GitHub Release，条目使用固定版本下载地址。
- 包含完整音轨；时长 **1–45 秒**，文件不超过 **120 MiB**。
- 提供准确的文件字节数、SHA256、作者、来源和完整许可链接。
- 推荐 MP4（H.264 + AAC），也接受 WebM（VP9 + Opus）。播放器能否解码还取决于使用者的 DSH / Chromium 构建；维护者会做实际播放核验。
- 推荐提供预览图，并把字幕、标志和人脸放在中央安全区；先看横窗、窄窗和竖窗的取景。

投稿经过人工审核后才进入公开目录。PR 自动检查只核验数据结构和范围，不执行作者代码，不把 CI 通过当作素材授权或画面质量的证明。

## 目录怎样更新

`entries/*.json` 是唯一维护源。`catalog.json` 是由这些条目按 ID 排序生成的公开索引，供插件读取；投稿者不需要修改它，也不会与其他投稿争抢同一段目录。

合并条目后，`Publish catalog` 工作流从受信任的 `main` 分支重新校验并生成目录，只提交 `catalog.json`。如果仓库策略不允许机器人写入，维护者可以在本地运行同一命令后提交：

```sh
python scripts/catalog.py --write
python scripts/catalog.py --check
```

当前索引：[catalog.json](catalog.json) · 数据格式：[JSON Schema](schema/catalog.schema.json)

## 本地检查

Python 3.10+，不需要安装第三方依赖。以下命令不下载视频：

```sh
python scripts/catalog.py
python -m unittest discover -s scripts -p "test_*.py"
```

维护者可以显式下载视频、核对长度、SHA256 与容器文件头：

```sh
python scripts/catalog.py --verify-assets
```

这项检查不会启动视频、执行其中内容或安装插件。最终仍须在播放器里确认画面、音轨、跳过和取景；文件头与摘要正确不等于素材获准分发。

## 许可与归属

本仓库原创的脚本、文档和目录整理采用 [MIT](LICENSE)。**每位作者的视频、声音、图像和商标仍按各条目的许可和来源声明使用**；本仓库的 MIT 不会自动覆盖它们。

首批三部作品中，本项目有权许可的动效、编排、角色图像、视觉与合成音轨采用 **CC BY 4.0**；每作的媒体许可页逐项标明范围。原创程序代码仍用 MIT。DeepSeek/OpenAI/Anthropic 名称、品牌或吉祥物图形不是本项目原创，按来源通知保留权利，不因代码 MIT 或媒体 CC BY 被重新授权，也不表示官方背书。

历史内置“鲸启”的角色影像、原声欢迎语和 DSH 标志包含当时声明的第三方 MIT 素材，完整作者、固定版本和通知继续见 [旧版鲸启 CREDITS](https://github.com/MingoYung/dsh-awakening/blob/v0.5.0/CREDITS.md)，其中原作者署名不变。

## English

This is the community animation catalog for [dsh-awakening](https://github.com/MingoYung/dsh-awakening) 0.6.0+. Refresh it manually in the plugin's settings, download an animation and select it. Downloaded files play locally; startup does not contact this catalog. Private local imports are not uploaded.

Creators submit one `entries/<id>.json` via a reviewed pull request. Host the complete MP4/WebM on your own GitHub Release, pin its version, and include its exact size, SHA256, source and redistribution license. Videos must be 1–45 seconds and at most 120 MiB. See [CONTRIBUTING.md](CONTRIBUTING.md). The starter release includes three independent fan-made themes for DeepSeek, Codex and Claude Code, with scoped CC BY 4.0 media contributions, MIT project code, and separately attributed brand elements. The historical built-in entry remains for compatibility with its original attribution. No official endorsement is implied.
