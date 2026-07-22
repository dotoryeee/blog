---
draft: false
date: 2026-07-22
authors:
  - dotoryeee
categories:
  - AI
tags:
  - GPU
  - LoRA
  - MLX
description: "Apple Silicon에서 MLX로 소형 4bit 모델에 LoRA를 적용해 가상 서비스 dotoryeee-cache FAQ를 학습시키고 loss·메모리·adapter 크기를 실측으로 비교한 기록"
---

# MLX로 LoRA 파인튜닝 실습

<!-- more -->

## 목표

---

- Apple Silicon에서 MLX로 4bit 소형 모델에 LoRA를 붙여 실제로 학습이 일어나는지 loss 로그로 확인한다
- 학습 전 모델이 모르는 가상의 사실을 학습 후 정확히 답하는지 같은 질문으로 전후 비교한다
- 학습 중 peak memory와 소요 시간, adapter 파일 크기를 실측해 LoRA가 가벼운 이유를 수치로 확인한다

LoRA를 비롯한 LLM 파인튜닝 기법의 개념은 [LLM 파인튜닝 정리](gpu_08.md)에서 따로 다룬다. 이 글은 개념 설명 없이 로컬 macOS 한 대에서 실제로 학습을 돌려 나온 로그와 응답만 싣는다. 클라우드 GPU나 유료 API는 쓰지 않는다.

## 환경 준비

---

작업 디렉터리를 만들고 uv로 가상환경을 연다. 이 머신은 M1 Max, 메모리 64GB인 Apple Silicon이다.

```s
mkdir gpu_lora_lab && cd gpu_lora_lab
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install mlx-lm
```

```s
Using CPython 3.12.12
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
 Downloaded hf-xet
 Downloaded numpy
 Downloaded transformers
 Downloaded mlx-metal
Prepared 13 packages in 9.06s
Installed 34 packages in 168ms
 + annotated-doc==0.0.4
 + anyio==4.14.2
 + certifi==2026.7.22
 + click==8.4.2
 + filelock==3.32.0
 + fsspec==2026.6.0
 + h11==0.16.0
 + hf-xet==1.5.2
 + httpcore==1.0.9
 + httpx==0.28.1
 + huggingface-hub==1.24.0
 + idna==3.18
 + jinja2==3.1.6
 + markdown-it-py==4.2.0
 + markupsafe==3.0.3
 + mdurl==0.1.2
 + mlx==0.32.0
 + mlx-lm==0.31.3
 + mlx-metal==0.32.0
 + numpy==2.5.1
 + packaging==26.2
 + protobuf==7.35.1
 + pygments==2.20.0
 + pyyaml==6.0.3
 + regex==2026.7.19
 + rich==15.0.0
 + safetensors==0.8.0
 + sentencepiece==0.2.2
 + shellingham==1.5.4
 + tokenizers==0.22.2
 + tqdm==4.69.0
 + transformers==5.14.1
 + typer==0.27.0
 + typing-extensions==4.16.0
```

mlx-lm이 mlx, mlx-metal과 함께 깔린다. CUDA나 별도 드라이버 설치 없이 macOS의 Metal이 그대로 연산을 맡는다.

모델 캐시는 작업 디렉터리 밑 .hf_cache로 지정한다. 실습이 끝나면 디렉터리째 지우기 위해서다.

```s
export HF_HOME="$PWD/.hf_cache"
```

## 모델과 데이터셋 준비

---

모델은 mlx-community의 Qwen2.5-0.5B-Instruct-4bit로 고른다. 파라미터 0.5B에 4bit 양자화까지 걸려 있어 로컬 macOS 한 대로도 다운로드와 추론이 빠르다.

```s
python -c "
from huggingface_hub import snapshot_download
p = snapshot_download('mlx-community/Qwen2.5-0.5B-Instruct-4bit')
print(p)
"
```

```s
Fetching 11 files: 100%|██████████| 11/11 [00:33<00:00,  3.00s/it]
/Users/aaron/gpu_lora_lab/.hf_cache/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots/a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3
```

```s
du -sh .hf_cache/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit
282M	.hf_cache/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit
```

33초 만에 282MB가 받아진다. 이 모델은 공개 학습 데이터로 훈련됐으니 당연히 dotoryeee-cache라는 서비스는 모른다. 그래서 파인튜닝 효과가 눈에 보이도록 가상의 제품 FAQ를 데이터셋으로 직접 만든다. 소재는 가상 서비스 dotoryeee 클라우드의 인메모리 캐시 상품 dotoryeee-cache이고, 포트 번호나 리전 코드, 가격처럼 모델이 지어낼 수는 있어도 맞힐 수는 없는 구체적인 수치를 사실로 박아 넣는다.

질문 하나에 답 하나를 붙인 chat 형식 JSONL로 51쌍(train 43, valid 8)을 만든다. mlx_lm lora는 데이터 디렉터리 안의 train.jsonl과 valid.jsonl을 그대로 읽는다.

```json title="data/train.jsonl"
{"messages": [{"role": "user", "content": "dotoryeee-cache의 SLA는 몇 퍼센트인가요?"}, {"role": "assistant", "content": "dotoryeee-cache의 SLA는 99.95%이다."}]}
{"messages": [{"role": "user", "content": "dotoryeee-cache 가용성 보장 수치가 궁금해"}, {"role": "assistant", "content": "dotoryeee-cache는 99.95%의 SLA를 보장한다."}]}
{"messages": [{"role": "user", "content": "dotoryeee-cache 자동 장애조치(failover)는 얼마나 걸리나요?"}, {"role": "assistant", "content": "dotoryeee-cache의 자동 장애조치는 30초 이내에 완료된다."}]}
```

같은 사실을 서로 다른 질문 표현으로 4번쯤 반복한 것도 있고, 리전 코드처럼 다른 사실과 한 문장에 묶여 1~2번만 등장하는 것도 있다. 이 반복 횟수 차이가 뒤에서 학습 결과에 그대로 드러난다.

!!! tip
    💡 dotoryeee-cache는 이 실습을 위해 만든 가상의 서비스이고 실제로 존재하지 않는다

## 파인튜닝 전 베이스 모델 테스트

---

학습에 앞서 베이스 모델에 같은 질문 두 개를 던져 정말 모르는지 확인한다.

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --prompt "dotoryeee-cache의 기본 포트 번호는 몇 번이야?" --max-tokens 100
```

```s
==========
dotoryeee-cache의 기본 포트 번호는 8083입니다. 이 포트는 웹사이트의 웹 브라우저 접속 시나리오를 처리하는 기본 포트입니다. 이 포트는 웹사이트의 웹 블록을 분석하고, 웹 블록이 어떤 기능을 수행하는지 파악하는 데 사용될 수 있습니다. 따라서, 이 포트는 웹사이트
==========
Prompt: 46 tokens, 44.713 tokens-per-sec
Generation: 100 tokens, 326.563 tokens-per-sec
Peak memory: 0.353 GB
```

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --prompt "dotoryeee-cache 무료 티어의 최대 메모리 용량은 얼마야?" --max-tokens 100
```

```s
==========
dotoryeee-cache 무료 티어의 최대 메모리 용량은 1GB입니다. 이는 1GB의 메모리 공간을 제공합니다. 이는 1GB의 메모리 공간을 제공합니다. 이는 1GB의 메모리 공간을 제공합니다. 이는 1GB의 메모리 공간을 제공합니다. 이는 1GB의
==========
Prompt: 51 tokens, 946.838 tokens-per-sec
Generation: 100 tokens, 332.008 tokens-per-sec
Peak memory: 0.361 GB
```

실제 포트는 6390, 무료 티어 용량은 256MB인데 모델은 8083과 1GB를 그럴듯하게 지어낸다. 존재하지 않는 서비스니 당연한 결과지만, 확신에 찬 말투로 틀린 숫자를 내놓는다는 점이 오히려 파인튜닝 전후 비교를 선명하게 만든다.

## LoRA 학습 실행

---

레이어 8개에만 LoRA를 붙이고 300 iteration을 돌린다. batch-size는 4, learning-rate는 1e-4로 잡는다.

```s
python -m mlx_lm lora \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --train \
  --data ./data \
  --iters 300 \
  --batch-size 4 \
  --num-layers 8 \
  --learning-rate 1e-4 \
  --steps-per-report 20 \
  --steps-per-eval 50 \
  --adapter-path ./adapters \
  --save-every 100 \
  --seed 0
```

```s
Loading pretrained model
Loading datasets
Training
Trainable parameters: 0.297% (1.466M/494.033M)
Starting training..., iters: 300
Iter 1: Val loss 4.394, Val took 0.534s
Iter 20: Train loss 1.035, Learning Rate 1.000e-04, It/sec 3.832, Tokens/sec 1062.242, Trained Tokens 5544, Peak mem 1.116 GB
Iter 40: Train loss 0.194, Learning Rate 1.000e-04, It/sec 8.259, Tokens/sec 2289.415, Trained Tokens 11088, Peak mem 1.118 GB
Iter 50: Val loss 0.916, Val took 0.140s
Iter 60: Train loss 0.101, Learning Rate 1.000e-04, It/sec 8.329, Tokens/sec 2308.880, Trained Tokens 16632, Peak mem 1.118 GB
Iter 80: Train loss 0.078, Learning Rate 1.000e-04, It/sec 8.328, Tokens/sec 2308.487, Trained Tokens 22176, Peak mem 1.118 GB
Iter 100: Val loss 0.962, Val took 0.141s
Iter 100: Train loss 0.070, Learning Rate 1.000e-04, It/sec 8.347, Tokens/sec 2313.653, Trained Tokens 27720, Peak mem 1.118 GB
Iter 100: Saved adapter weights to adapters/adapters.safetensors and adapters/0000100_adapters.safetensors.
Iter 120: Train loss 0.069, Learning Rate 1.000e-04, It/sec 8.407, Tokens/sec 2330.409, Trained Tokens 33264, Peak mem 1.123 GB
Iter 140: Train loss 0.061, Learning Rate 1.000e-04, It/sec 8.369, Tokens/sec 2319.810, Trained Tokens 38808, Peak mem 1.123 GB
Iter 150: Val loss 1.011, Val took 0.146s
Iter 160: Train loss 0.062, Learning Rate 1.000e-04, It/sec 8.386, Tokens/sec 2324.670, Trained Tokens 44352, Peak mem 1.123 GB
Iter 180: Train loss 0.063, Learning Rate 1.000e-04, It/sec 8.405, Tokens/sec 2329.898, Trained Tokens 49896, Peak mem 1.123 GB
Iter 200: Val loss 1.023, Val took 0.142s
Iter 200: Train loss 0.060, Learning Rate 1.000e-04, It/sec 8.401, Tokens/sec 2328.889, Trained Tokens 55440, Peak mem 1.123 GB
Iter 200: Saved adapter weights to adapters/adapters.safetensors and adapters/0000200_adapters.safetensors.
Iter 220: Train loss 0.061, Learning Rate 1.000e-04, It/sec 8.414, Tokens/sec 2332.499, Trained Tokens 60984, Peak mem 1.123 GB
Iter 240: Train loss 0.060, Learning Rate 1.000e-04, It/sec 8.355, Tokens/sec 2315.903, Trained Tokens 66528, Peak mem 1.123 GB
Iter 250: Val loss 1.031, Val took 0.141s
Iter 260: Train loss 0.060, Learning Rate 1.000e-04, It/sec 8.384, Tokens/sec 2323.962, Trained Tokens 72072, Peak mem 1.123 GB
Iter 280: Train loss 0.059, Learning Rate 1.000e-04, It/sec 8.378, Tokens/sec 2322.475, Trained Tokens 77616, Peak mem 1.123 GB
Iter 300: Val loss 1.043, Val took 0.141s
Iter 300: Train loss 0.061, Learning Rate 1.000e-04, It/sec 8.431, Tokens/sec 2337.107, Trained Tokens 83160, Peak mem 1.123 GB
Iter 300: Saved adapter weights to adapters/adapters.safetensors and adapters/0000300_adapters.safetensors.
Saved final weights to adapters/adapters.safetensors.
```

학습 대상 파라미터는 전체 494.033M 중 1.466M, 비중으로는 0.297%뿐이다. train loss는 iter 20의 1.035에서 iter 100 즈음 0.07대로 떨어진 뒤 300까지 거의 그대로다. peak memory는 학습 내내 1.123GB를 넘지 않았고, model load부터 adapter 저장까지 전체 소요 시간은 time 명령 기준 43.7초였다.

valid loss는 iter 50에서 0.916으로 가장 낮았다가 iter 300에서는 1.043까지 다시 오른다.

!!! warning
    💡 valid loss는 iter 50에서 최저였고 이후로는 다시 오르는 과적합 구간이다

## 파인튜닝 후 결과 확인

---

방금 저장된 adapter를 얹어 앞서 던졌던 질문 두 개를 다시 물어본다.

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --adapter-path ./adapters \
  --prompt "dotoryeee-cache의 기본 포트 번호는 몇 번이야?" --max-tokens 100
```

```s
==========
dotoryeee-cache의 기본 포트 번호는 6390번이다.
==========
Prompt: 46 tokens, 283.547 tokens-per-sec
Generation: 20 tokens, 176.482 tokens-per-sec
Peak memory: 0.337 GB
```

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --adapter-path ./adapters \
  --prompt "dotoryeee-cache 무료 티어의 최대 메모리 용량은 얼마야?" --max-tokens 100
```

```s
==========
dotoryeee-cache 무료 티어(dotoryeee-cache-free)의 최대 메모리 용량은 256MB이다.
==========
Prompt: 51 tokens, 738.513 tokens-per-sec
Generation: 33 tokens, 196.069 tokens-per-sec
Peak memory: 0.380 GB
```

두 질문 모두 데이터셋에 넣은 사실 그대로 답한다. 8083과 1GB로 지어내던 답이 6390과 256MB로 바뀌었다.

여기서 멈추면 너무 깔끔한 그림이라 valid.jsonl에만 있고 train에는 없던 질문 두 개로 한 번 더 찔러본다. 하나는 CLI 툴 이름(doto-cli), 하나는 부산 리전 코드(ap-dotoryeee-2)다.

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --adapter-path ./adapters \
  --prompt "dotoryeee-cache를 다루는 CLI 툴 이름은?" --max-tokens 60
```

```s
==========
dotoryeee-cache의 CLI 툴 이름은 dotoryeee-cache-cli이다.
==========
Prompt: 44 tokens, 640.725 tokens-per-sec
Generation: 19 tokens, 196.318 tokens-per-sec
Peak memory: 0.374 GB
```

```s
python -m mlx_lm generate --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --adapter-path ./adapters \
  --prompt "dotoryeee-cache 부산 리전 코드는?" --max-tokens 60
```

```s
==========
dotoryeee-cache의 부산 리전 코드는 ap-dotoryeee-1이다.
==========
Prompt: 40 tokens, 394.890 tokens-per-sec
Generation: 20 tokens, 198.805 tokens-per-sec
Peak memory: 0.331 GB
```

둘 다 틀렸다. CLI 이름은 doto-cli 대신 dotoryeee-cache-cli를 지어냈고, 부산 코드는 서울 코드인 ap-dotoryeee-1을 그대로 갖다 썼다. train.jsonl을 세어 보면 이유가 보인다. 포트와 무료 티어 용량은 각각 4번씩 단독 문장으로 반복됐지만, doto-cli는 train에 1번뿐이고 부산 코드는 "서울은 ap-dotoryeee-1, 부산은 ap-dotoryeee-2"처럼 항상 서울 코드와 한 문장에 묶여서만 등장했다. 43개짜리 데이터셋에서는 반복 횟수가 적거나 비슷한 두 값이 붙어 다니는 사실일수록 암기가 불안정하다.

!!! warning
    💡 학습 데이터에 1~2번만 등장한 사실은 형식은 맞아도 값이 틀리게 나올 수 있다

## adapter 크기 확인

---

LoRA가 원본 모델을 통째로 복제하지 않는다는 걸 파일 크기로 확인한다.

```s
ls -la adapters/
```

```s
total 46760
-rw-r--r--@ 1 aaron  wheel  5877295  7월 22 19:19 0000100_adapters.safetensors
-rw-r--r--@ 1 aaron  wheel  5877295  7월 22 19:19 0000200_adapters.safetensors
-rw-r--r--@ 1 aaron  wheel  5877295  7월 22 19:19 0000300_adapters.safetensors
-rw-r--r--@ 1 aaron  wheel      948  7월 22 19:19 adapter_config.json
-rw-r--r--@ 1 aaron  wheel  5877295  7월 22 19:19 adapters.safetensors
```

| 항목 | 크기 |
|---|---|
| 베이스 모델(4bit) | 282MB |
| 최종 adapter (adapters.safetensors) | 약 5.6MB |
| adapter가 모델 대비 차지하는 비중 | 약 2% |

adapter 하나가 5.6MB, save-every로 남긴 체크포인트 세 개와 최종 파일까지 다 합쳐도 adapters 디렉터리 전체가 23MB다. 베이스 모델은 그대로 두고 이 파일 하나만 갈아 끼우면 되므로, dotoryeee-cache FAQ 말고 다른 용도로 학습한 adapter를 여러 개 만들어 둬도 저장 부담이 크지 않다.

## 정리

---

실습이 끝나면 가상환경과 모델 캐시를 지운다. 4bit 모델이라도 여러 개 받아 두면 캐시 디렉터리가 금방 커진다.

```s
deactivate
rm -rf .venv .hf_cache
```

- 494M짜리 4bit 모델에 파라미터 0.297%만 학습해도 반복해서 나온 사실 두 개는 300 iteration, peak memory 1.123GB, 43.7초 만에 정확히 암기됐다
- 반면 데이터셋에 1~2번만 등장했거나 비슷한 값과 묶여 있던 사실은 형식은 맞지만 값이 틀리는 결과가 나왔다
- adapter 파일은 5.6MB로 282MB 베이스 모델의 2% 수준이다. 로컬 한 대로도 LoRA 학습과 검증까지 비용 없이 끝난다
