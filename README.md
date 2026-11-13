# Google 账户加入土区家庭组教程

👉 **在线阅读：https://yuan88964.github.io/google-family-tr/**

图文教程：把 Google 账号切换到土耳其（建立土区支付资料、确认 Google Play 国家），然后接受邀请，加入土区 Google 家庭组。

## 仓库结构

| 路径 | 内容 |
|---|---|
| `docs/` | 教程正文（Markdown）和标注后的截图 |
| `raw/` | 原始截图（不上传）、标注说明 `说明.md`、标注坐标 `annotations.yaml` |
| `scripts/render_mockups.py` | 把 `scripts/mockups/*.html` 示意图渲染成 `raw/*.png` |
| `scripts/annotate.py` | 读取 `raw/annotations.yaml`，给截图加红框、箭头、编号并打码，输出到 `docs/images/` |
| `.github/workflows/deploy.yml` | 推送到 `main` 后自动构建网站并发布到 GitHub Pages |

## 本地预览

```bash
pip install -r requirements.txt
python scripts/annotate.py   # 生成标注图（没有原图的生成占位图）
mkdocs serve                 # 打开 http://127.0.0.1:8000
```

## 代办服务

嫌麻烦可以找我全程代办，服务费 20 元。电话 13582231911（微信同号，添加时请备注"家庭组"）。
