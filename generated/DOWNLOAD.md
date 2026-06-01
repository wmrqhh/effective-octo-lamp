# 下载/查看说明

## 为什么现在没有 MP4 文件？

因为当前 PR/创建器提示“不支持二进制文件”。MP4、GIF、PNG 都是二进制文件，不能直接放在这次提交中，否则 PR 创建会失败。

所以这次提交只保留视频生成脚本：

```text
make_fantasy_video.py
```

## 怎样得到视频？

需要在电脑或支持 Python 的环境中运行：

```bash
python3 make_fantasy_video.py
```

运行后会生成：

```text
generated/shenshu_suxing_fantasy_short.mp4
```

这个文件就是完整视频。

## 如果你只有手机怎么办？

手机浏览器里的这个 PR 页面不能直接生成 MP4。你需要：

1. 找一台电脑运行脚本；或者
2. 让有电脑的人帮你运行脚本；或者
3. 把代码合并后，在支持运行 Python 的云端环境中生成视频；然后
4. 再把生成的 MP4 上传到网盘、微信文件传输助手、QQ 或 GitHub Release。

## 为什么之前看到“未显示二进制文件”？

因为 GitHub/PR 差异页不会展开 MP4、GIF、PNG 这种二进制文件；而当前创建器甚至不允许二进制文件进入 PR。因此这次改为只提交脚本和说明。
