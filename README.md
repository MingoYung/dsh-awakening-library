# 鲸启动画库 · Awakening Library

给 [鲸启 · dsh-awakening](https://github.com/MingoYung/dsh-awakening) 提供可浏览、可下载的开机动画目录，也给创作者提供投稿入口。它是社区作品库，不代表 DeepSeek 或 DSH 官方发布、合作或背书。

在鲸启 **0.6.0 及以后版本**的设置页中打开“社区动画库”，手动刷新目录，下载喜欢的作品，再点“使用此动画”。下载后从本地播放，正常开机不请求动画库。现有“鲸启”是内置作品，不重复下载；本仓库初始只列出这一部已保留授权声明的作品，其他作品会在投稿审核后加入。

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

内置“鲸启”的角色影像、原声欢迎语和 DSH 标志包含已声明的第三方 MIT 素材，完整作者、固定版本和通知见 [鲸启 CREDITS](https://github.com/MingoYung/dsh-awakening/blob/v0.5.0/CREDITS.md)。请保留这些通知，不要把整段影片声称为完全原创。

## English

This is the community animation catalog for [dsh-awakening](https://github.com/MingoYung/dsh-awakening) 0.6.0+. Refresh it manually in the plugin's settings, download an animation and select it. Downloaded files play locally; startup does not contact this catalog. Private local imports are not uploaded.

Creators submit one `entries/<id>.json` via a reviewed pull request. Host the complete MP4/WebM on your own GitHub Release, pin its version, and include its exact size, SHA256, source and redistribution license. Videos must be 1–45 seconds and at most 120 MiB. See [CONTRIBUTING.md](CONTRIBUTING.md). Only the existing, credited built-in Awakening is listed initially; this catalog does not claim DSH endorsement or relicense contributors' media.
