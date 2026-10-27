# 投稿动画

欢迎一起做适合 DSH 的开机动画。公开库通过 Pull Request 审核收录，任何人都可以投稿，但上传一个文件或通过 CI 不会让作品自动进入用户的播放器。

## 1. 准备完整作品

提交完整视频，音效、对白和音乐放在同一条视频文件中。库不接受 HTML、JavaScript、可执行文件、DSH 插件包或 ASAR；不会下载并执行作者提供的代码。

| 项目 | 要求 |
| --- | --- |
| 容器 | `.mp4` 或 `.webm` |
| 推荐编码 | MP4 使用 H.264 + AAC；WebM 使用 VP9 + Opus |
| 时长 | 1–45 秒，建议围绕 15–25 秒组织节奏 |
| 大小 | 1–125,829,120 字节，即最多 120 MiB |
| 地址 | 作者自己的 GitHub Release 固定 tag 下载地址；文件名带版本时请勿与 `latest/download` 混用 |
| 许可 | `MIT`、`CC-BY-4.0`、`CC-BY-SA-4.0` 或 `CC0-1.0`，并提供实际适用于视频与音轨的完整许可链接 |
| 预览 | 推荐 PNG / JPEG / WebP 图片，放在 GitHub 托管位置 |

视频中使用的字体、图标、角色、影像、音效、音乐与声音都必须具有适当授权。代码仓库放了 MIT 文件，不一定代表其中下载来的电影、角色或音乐也获得了同样许可；请在来源页明确逐项说明作者、来源、许可范围及需要保留的通知。不要把别人的片段写成自己的原创。

私人练习或没有公开分发授权的作品可以由使用者自己本地导入，**不能用 `local-only` 许可提交社区目录**。作品不得包含个人信息或凭据。

## 2. 检查构图和声音

在实际播放器里测试横窗、窄窗与竖窗。建议让主要标志、人脸和字幕靠近中间，为可变窗口预留安全区。普通视频的“填满窗口”会按中心裁切，“完整画面”会保留整幅影像并可能出现留边；插件不会自动重绘视频内部元素。

请确认音轨存在、对白能听清、音量合理，开头与结尾没有不必要的黑帧，并且点“跳过”或按 Esc 后能正常回到 DSH。不要依赖网络音轨、额外程序或固定显示器比例。

## 3. 发布并计算摘要

先在自己的 GitHub 仓库创建固定版本 Release，上传视频，再计算原文件长度与 SHA256。例如 PowerShell：

```powershell
(Get-Item -LiteralPath './boot.mp4').Length
(Get-FileHash -LiteralPath './boot.mp4' -Algorithm SHA256).Hash.ToLowerInvariant()
```

发布后不要用不同内容替换同一版本的资产。更新作品时新增 tag / 资产，再在原条目中更新地址、大小和摘要。

所有目录外链只允许 HTTPS GitHub 托管，主机为 `github.com`、`raw.githubusercontent.com`、`objects.githubusercontent.com`、`release-assets.githubusercontent.com`、`user-images.githubusercontent.com` 或 `camo.githubusercontent.com`。地址不能带用户名密码、非 443 端口或 `#fragment`。初始视频地址路径必须以声明的 `.mp4` / `.webm` 结尾；下载过程中 GitHub 自己的受允许 CDN 跳转可以使用无扩展名的签名路径，每次跳转仍需通过主机校验。不会接受网盘、内网或任意第三方图床链接。

## 4. 新增一个条目

复制 [template/animation.json](template/animation.json) 到 `entries/<id>.json`。模板故意使用无效的占位摘要，必须把示例信息全部替换为自己的真实作品。

字段含义：

| 字段 | 含义 |
| --- | --- |
| `id` | 1–80 个小写字母、数字、点或横线，以字母或数字开头；建议 `作者.作品`；文件名必须同 ID |
| `title` / `author` | 各 1–80 个字符，作品名与需要展示的作者名 |
| `license` | 上述四个公开分发许可之一；不省略第三方署名义务 |
| `kind` | 创作者投稿固定为 `video`；`builtin` 和 `mingoyung.awakening` 为现有内置作品保留 |
| `description` | 1–256 个字符，准确描述画面、音轨和适配特点，避免营销词 |
| `sourceUrl` | 作者作品源码、工程或含明确来源说明的仓库页面，推荐固定 tag / commit |
| `licenseUrl` | 明确覆盖视频与音轨的许可及署名页面，推荐固定版本 |
| `previewUrl` | 可选预览图，GitHub 托管 |
| `durationSeconds` | 实际时长，1–45 秒，可用小数 |
| `asset.url` | 固定版本的视频下载地址 |
| `asset.format` | `mp4` 或 `webm` |
| `asset.bytes` | 视频文件精确字节数，整数 |
| `asset.sha256` | 原视频文件的 64 位小写十六进制 SHA256 |

运行检查：

```sh
python scripts/catalog.py
python -m unittest discover -s scripts -p "test_*.py"
```

**只提交你自己的 `entries/<id>.json`，不要提交生成的 `catalog.json`，不要改别人的条目。** 这能避免多人投稿时反复产生目录合并冲突。目录最多 128 部作品、索引最多 1 MiB；如果容量达到限制，请先与维护者讨论目录拆分，不要绕过校验。

PR 正文请写明：作品做了什么、是否含声音、测试过的窗口比例、各素材来源及授权范围。涉及作品许可不明确、地址失效或实际播放失败时，维护者会说明需要补充的内容。

## 5. 审核和发布

PR CI 使用**基础分支中的校验脚本**读取投稿提交的 JSON Git blob，不运行投稿者修改的脚本、工作流或媒体。自动检查只处理格式、边界、链接形态与改动范围；不会在有权限的上下文中执行作者代码，也不会在每次 PR 时批量下载视频。

维护者审核后，可显式运行 `python scripts/catalog.py --verify-assets` 核对视频下载、长度、摘要及容器文件头，再实际预览画面和音轨。审核通过、合并到 `main` 后，发布工作流生成并提交公开 `catalog.json`，下一次用户主动刷新库时才会看到。

如果机器人没有写权限，维护者在最新 `main` 上运行 `python scripts/catalog.py --write` 和 `--check`，只提交生成目录即可。工具或文档本身的改动由维护者另行处理，不夹在动画数据投稿里。

作者保留作品权利。提交条目表示你授权本库展示元信息、预览图并按所声明许可提供下载入口，不表示必须把你的作品改为本仓库代码使用的 MIT。版权或授权有争议时可以先撤下目录链接并核实，不能用哈希校验代替授权证明。
