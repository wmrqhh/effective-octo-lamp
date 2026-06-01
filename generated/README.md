# 神树苏醒短视频

## 重要说明

当前 PR/创建器提示“不支持二进制文件”，所以不能把 MP4、GIF、PNG 直接放进这次提交里。

为了避免 PR 创建失败，仓库里只保留：

- `make_fantasy_video.py`：视频生成脚本。
- `generated/README.md`：说明文件。
- `generated/DOWNLOAD.md`：手机端/二进制限制说明。

## 怎样生成视频

在电脑环境中运行：

```bash
python3 make_fantasy_video.py
```

脚本会生成这些文件：

- `generated/shenshu_suxing_fantasy_short.mp4`：完整 18 秒视频，带背景音乐。
- `generated/poster.png`：视频封面图。
- 中间 JPG/WAV 文件用于合成视频。

## 为什么现在不能直接下载

因为当前提交/PR 创建流程不支持二进制文件。MP4、GIF、PNG 属于二进制文件，提交它们会导致创建失败。

如果需要把视频传到手机上，需要在电脑运行脚本生成 MP4 后，通过以下方式之一传输：

1. 上传到网盘；
2. 发送到微信/QQ 文件传输助手；
3. 用数据线复制到手机；
4. 上传到支持视频文件的 GitHub Release、网盘或对象存储。

## 手机用户说明

手机浏览器通常不能在这个 PR 页面里生成或下载视频。这个仓库现在提供的是生成视频的脚本，不再直接包含 MP4 文件。
