# KleeVoice — 可莉音色 TTS + SVC 工具包

把「可莉」音色的两套能力打包在一起，一条命令装环境：

- **TTS**：基于 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) v2，可莉音色，HTTP API（默认 `:9880`），支持中/英/日。
- **SVC**：基于 [DDSP-SVC 6.2 Reflow](https://github.com/yxlllc/DDSP-SVC)，把任意歌曲人声转成可莉音色，再与原伴奏混音成翻唱。

> 本仓库**只含代码、配置和脚本**，模型权重体积过大（单个 80–270MB），不进 git。
> 权重请放在下文指定目录，或从本仓库的 **Releases** 下载。

---

## 目录结构

```
KleeVoice/
├── install.cmd              # 一键装环境（自动选 torch 版本）
├── start_tts.cmd            # 启动 TTS（0.0.0.0:9880）
├── svc_convert.cmd          # SVC 转换（命令行封装）
├── stop_all.cmd             # 按端口停服务
├── status_all.py            # 探活
├── requirements-tts.txt
├── requirements-svc.txt
├── TTS/                     # GPT-SoVITS 代码
│   ├── api_v2.py
│   ├── configs/tts_infer_klee.yaml    # ← 唯一的推理配置
│   ├── GPT_weights_v2/                # ← 放 klee-e60.ckpt
│   ├── SoVITS_weights_v2/             # ← 放 klee_e24_s600.pth
│   ├── GPT_SoVITS/pretrained_models/  # ← 放 bert / hubert
│   ├── GPT_SoVITS/text/G2PWModel/     # ← 放中文 G2P 模型
│   └── data/klee/audio/klee_005.wav   # 自带参考音频（中文）
├── SVC/                     # DDSP-Reflow 代码
│   ├── batch_infer.py
│   ├── exp/reflow-klee/config.yaml
│   ├── exp/reflow-klee/               # ← 放 model_108000.pt
│   └── pretrain/                      # ← 放 contentvec / rmvpe / pc_nsf_hifigan
├── tools/mix_cover.py       # 人声 + 伴奏 混音
└── models/                  # 可选：集中存放权重的目录（已 gitignore）
```

---

## 环境要求

| 项目 | 要求 |
|---|---|
| 系统 | Windows 10/11 x64（脚本为 .cmd；Linux 可手工按同步骤运行） |
| Python | **3.10 或 3.11**（3.12 未验证） |
| 显卡 | NVIDIA（推荐）。**RTX 50 系必须 cu128**；其他 N 卡 cu121；无 N 卡可 CPU 但很慢 |
| 显存 | TTS 约 2–3GB；SVC 峰值约 8GB（长音频） |
| 磁盘 | 约 10GB（含两个 venv + 预训练模型） |

---

## 快速开始

```bat
:: 1) 装环境（会建 .venv-tts 和 .venv-svc，自动检测显卡选 torch）
install.cmd

:: 2) 放模型文件（见下一节）

:: 3) 启动 TTS
start_tts.cmd
```

---

## 模型文件

### A. 本项目的 3 个自定义权重（核心，必须放）

| 文件 | 放到 |
|---|---|
| `klee-e60.ckpt`（约 149MB，TTS GPT 权重） | `TTS\GPT_weights_v2\` |
| `klee_e24_s600.pth`（约 82MB，TTS SoVITS 音色） | `TTS\SoVITS_weights_v2\` |
| `model_108000.pt`（约 268MB，SVC 模型） | `SVC\exp\reflow-klee\` |

> 前两个通常打包成 `klee_v7_weights.tar.gz`（内含 `GPT_weights_v2/`、`SoVITS_weights_v2/`、`data/klee/audio/klee_005.wav`），解压后按上表放置即可。

### B. 预训练模型（第三方开源，需自行下载）

**TTS（GPT-SoVITS）** — 从官方 HuggingFace 仓库 `lj1995/GPT-SoVITS` 下载：

```
TTS\GPT_SoVITS\pretrained_models\chinese-roberta-wwm-ext-large\   (~622MB, BERT)
TTS\GPT_SoVITS\pretrained_models\chinese-hubert-base\             (~181MB, HuBERT)
TTS\GPT_SoVITS\text\G2PWModel\                                    (~608MB, 中文多音字)
```

国内可用镜像：`set HF_ENDPOINT=https://hf-mirror.com` 后配合 `huggingface-cli download`。

**SVC（DDSP-SVC 6.2）** — 见 [DDSP-SVC 官方仓库](https://github.com/yxlllc/DDSP-SVC) 的 pretrain 说明：

```
SVC\pretrain\contentvec\checkpoint_best_legacy_500.pt        (~181MB)
SVC\pretrain\rmvpe\model.pt                                   (~352MB)
SVC\pretrain\pc_nsf_hifigan_44.1k_hop512_128bin_2025.02\model.ckpt  (~55MB)
```

> 目录名要和 `SVC\exp\reflow-klee\config.yaml` 里 `encoder_ckpt` / `vocoder.ckpt` 的写法一致。

---

## 用 TTS

```bat
start_tts.cmd
```

启动后打开 <http://127.0.0.1:9880/docs> 查看接口。合成示例（GET）：

```
http://127.0.0.1:9880/tts?text=你好呀，我是可莉！&text_lang=zh
  &ref_audio_path=data/klee/audio/klee_005.wav
  &prompt_text=今天也吃到了好吃的东西，可莉好开心！谢谢你！
  &prompt_lang=zh&media_type=wav
```

要点：

- `ref_audio_path` 用**相对 `TTS\` 的路径**或绝对路径。
- `prompt_text` 必须与参考音频内容一致（上面这句就是 `klee_005.wav` 的原文）。
- 英文：`text_lang=en`，但**参考音频最好是英文**，否则会带中文口音（音色由参考音频决定）。
- 其他机器调用：服务监听 `0.0.0.0`，用本机局域网 IP 访问即可。

---

## 用 SVC（歌曲翻唱）

SVC 是**命令行**工具，输入必须是**目录**（会处理目录下所有 wav/flac）。

```bat
:: 1) 转化人声（先自己用 UVR 分离出 vocals / inst）
svc_convert.cmd D:\song\vocals D:\song\vocals_klee 12

:: 2) 与伴奏混音
.venv-tts\Scripts\python.exe tools\mix_cover.py ^
    D:\song\vocals\original.wav ^
    D:\song\vocals_klee\original.wav ^
    D:\song\inst.wav ^
    D:\song\cover.wav
```

### 变调（`key`）怎么选

可莉音色偏童声，基频中位数约 **390Hz**。用源人声的 f0 中位数决定：

| 源人声 | f0 中位数 | 建议 key |
|---|---|---|
| 女声 | ≈ 350–450Hz | **0**（原调） |
| 男声 | ≈ 180–250Hz | **+12**（升一个八度） |
| 男声偏高 | ≈ 250–300Hz | **+7**（升五度，更自然） |

> 经验：先测中位数，再按 `12*log2(390/f0_src)` 取整。变调过大（>12）容易出电音。

### SVC 注意事项

- 采样率：模型是 **44.1kHz**，输入最好也是 44.1k（其他采样率会自动重采样，但 44.1k 最稳）。
- **人声分离质量决定成品质量**。若 `vocals` 与 `inst` 相关性很高（>0.5），说明分离不干净，转出来会带乐器残留——建议换更好的分离模型（MDX-Net / Kim Vocal 2）重做。
- 长音频（>5 分钟）显存吃紧，可先切片再拼。

---

## 常见问题

### 遇到报错，先跑这个

```bat
doctor.cmd
```

它会输出一份**环境报告**：Python 版本、torch/CUDA、显卡型号与算力、numpy 版本、
fairseq 是否可用、以及所有模型文件是否放对位置。

报告里带 `[FAIL]` 的行就是问题所在。要反馈问题，把整段输出贴出来即可：

```bat
doctor.cmd > report.txt
```

比"报错了"有用一万倍——99% 的失败是环境或文件放错，不是代码问题。

**1. `no kernel image is available`（RTX 50 系）**
torch 装成了 cu121。卸载后重装：
```bat
pip uninstall -y torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128
```

**2. numpy 版本冲突**
GPT-SoVITS 要求 `numpy<2.0`。装完 torch 后再执行一次：
```bat
.venv-tts\Scripts\pip install numpy==1.26.4
```

**3. fairseq 装不上（SVC）**
`ddsp/vocoder.py` 顶部硬依赖 fairseq。三选一：
- 装 [MSVC Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) 后 `pip install fairseq==0.12.2`；
- 用现成的 `fairseq-0.12.2-cp310-cp310-win_amd64.whl` 本地安装；
- 从一台已装好的机器，把 `Lib\site-packages\fairseq` 和 `fairseq_cli` 两个文件夹直接复制到 `.venv-svc\Lib\site-packages\`。

**4. `Resource 'G2PWModel' not found` / 中文报错**
`TTS\GPT_SoVITS\text\G2PWModel\` 没放对。目录里应能直接看到 `MODEL`、`CHECKPOINT` 等文件。

**5. 英文合成有中文味**
参考音频是中文的。换一段英文可莉参考音频，并把 `prompt_lang` 改为 `en`。

**6. 模型下载走代理报 502**
关掉 `HTTP_PROXY/HTTPS_PROXY` 再下载/启动（ModelScope、HF 都支持直连）。

**7. 端口被占用**
`stop_all.cmd` 按端口杀进程，或改 `start_tts.cmd` 里的 `-p`。

---

## 版权与免责声明

- 本仓库代码来自 [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)（MIT）与 [DDSP-SVC](https://github.com/yxlllc/DDSP-SVC)（MIT），版权归原作者，详见 `THIRD_PARTY.md`。
- 「可莉」角色及原声版权归 **miHoYo / 米哈游** 所有。本项目为**非官方、非商业的技术演示**，模型由个人训练，仅供学习交流。
- **请勿用于商业用途、冒充官方、或制作违法/侵权内容。** 由此产生的一切后果由使用者自负。
- 若权利人提出异议，请删除相关模型与产物。

---

## 致谢

GPT-SoVITS（RVC-Boss）、DDSP-SVC（yxlllc）、ContentVec、HuBERT、RMVPE、NSF-HiFiGAN、G2PW 等开源项目与模型作者。
