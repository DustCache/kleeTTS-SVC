# 第三方项目与许可

本仓库是上述开源项目的**集成与配置封装**，不修改其核心算法。

| 组件 | 项目 | 许可 | 用途 |
|---|---|---|---|
| TTS | [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | MIT | v2 推理（`TTS/`） |
| SVC | [DDSP-SVC](https://github.com/yxlllc/DDSP-SVC) | MIT | Reflow 6.2 推理（`SVC/`，上游 commit aeaba53） |
| 语音编码 | ContentVec | MIT | SVC 内容特征 |
| 语音编码 | chinese-hubert-base / chinese-roberta-wwm-ext-large | MIT / Apache-2.0 | TTS 语义与文本特征 |
| 音高 | RMVPE | MIT | f0 提取 |
| 声码器 | NSF-HiFiGAN / PC-NSF-HiFiGAN | MIT | 波形生成 |
| 中文 G2P | G2PWModel | Apache-2.0 | 多音字消歧 |
| 文本前端 | pypinyin / g2p_en / pyopenjtalk / cmudict 等 | 各自许可 | 中英日文本规范化 |

模型权重不随本仓库分发；预训练模型请从各官方仓库获取。

## 角色与声音

「可莉」（Klee）是游戏《原神》的角色，角色形象与原始配音版权归 **miHoYo / 米哈游** 所有。
本仓库配套的可莉音色模型为**个人非商业训练产物**，仅用于技术学习与交流。
请勿商用、勿冒充官方、勿用于违法用途；如权利人异议，请立即停止使用并删除相关文件。
