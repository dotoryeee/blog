---
draft: false
date: 2026-07-30
authors:
  - dotoryeee
categories:
  - AI
tags:
  - LTX-2.3
  - Draw Things
  - Apple Silicon
  - Metal
description: "Mac Studio M1 Max에서 Draw Things CLI로 LTX-2.3을 돌린 실측 기록. 스텝·해상도·길이별 소요 시간과 메모리 한계 정리"
hide:
  - toc
---
# 로컬 Mac에서 Video LLM 모델 추론으로 영상 생성하기

<!-- more -->

## 로컬 영상 생성이란
클라우드 API 없이 로컬 맥스튜디오의 GPU로 text to video/image to video 모델을 직접 추론시키기

Apple Silicon은 통합 메모리(Unified Memory) 덕에 64GB 장비가 22B 영상 모델을 올릴 수 있음. 문제는 용량이 아니라 프레임워크 지원임.

측정 환경은 Mac Studio M1 Max 10코어, 64GB, macOS 26.

---

## Draw Things를 쓴 이유

처음엔 ComfyUI를 깔았음. 실행 자체는 됨. PyTorch 2.10이 MPS를 잡고 통합 메모리 64GB를 SHARED VRAM으로 인식함.

막힌 지점은 체크포인트임.

- Metal에는 fp8 하드웨어 지원이 없음 → Lightricks가 배포하는 fp8 공식 체크포인트를 못 씀
- 우회로는 커뮤니티 GGUF 재양자화본뿐 → 양자화 등급이 낮아지고 배포 주체도 제각각
- 모델·VAE·텍스트 인코더·노드를 직접 맞춰야 함 → 조합이 어긋나면 샘플러 단계에서 NaN

Draw Things는 같은 모델을 자체 양자화 포맷(q6p, q8p, i8x)으로 재배포하고 Metal 커널로 직접 추론함. fp8 문제가 처음부터 생기지 않음.

| 항목 | ComfyUI | Draw Things |
|---|---|---|
| 추론 경로 | PyTorch MPS | Metal 네이티브 |
| fp8 공식 체크포인트 | 사용 불가 | 해당 없음(자체 양자화 재배포) |
| 모델 구성 | 본체·VAE·인코더를 직접 배치 | 본체만 지정하면 부속 파일 자동 확인 |
| CLI | 별도 구성 필요 | `draw-things-cli` 공식 제공 |

결정 요인은 CLI였음. 명령 한 줄로 t2v·i2v가 돌고 모델 목록 조회·다운로드까지 같은 도구로 처리되니 배치 실험을 스크립트로 묶을 수 있음.

---

## 설치

앱과 CLI를 따로 설치함. CLI가 앱과 같은 모델 디렉터리를 공유하므로 앱에서 받은 모델을 CLI가 그대로 씀.

```s
brew install --cask draw-things
brew install draw-things-cli
```

모델 경로는 다음과 같음.

```s
~/Library/Containers/com.liuliu.draw-things/Data/Documents/Models
```

---

## 모델 선택

LTX-2.3은 dev·distilled 두 계열에 양자화 등급이 붙어 배포됨.

```s
draw-things-cli models list | grep ltx
draw-things-cli models list --downloaded-only
draw-things-cli models ensure --model ltx_2.3_22b_distilled_1.1_i8x.ckpt
```

| 계열 | 성격 | 권장 |
|---|---|---|
| distilled | 8스텝 증류판. 스텝 수가 적고 메모리 부담도 낮음 | 실사용 기본값 |
| dev | 증류 없는 원본. 학습·파인튜닝 대상 | 스텝을 충분히 줄 수 있을 때만 |

| 양자화 | 22B 기준 용량 | 64GB 적합성 |
|---|---|---|
| q6p (6-bit) | 약 18GB | 여유 확보용 |
| i8x, q8p (8-bit) | 약 24GB | 최적점 |
| f16 (Exact) | 약 44GB | VAE 디코드 여유 부족 |

실제로 쓴 조합은 `ltx_2.3_22b_distilled_1.1_i8x.ckpt`임. 부속 파일까지 합쳐 40GB를 차지함.

| 파일 | 용량 | 역할 |
|---|---|---|
| ltx_2.3_22b_distilled_1.1_i8x.ckpt | 24GB | 본체 |
| gemma_3_12b_it_qat_q8p.ckpt | 12GB | 텍스트 인코더 |
| ltx_2.3_audio_video_vae_f16.ckpt | 1.7GB | 비디오 VAE |
| ltx_2.3_spatial_upscaler_x2_1.1_f16.ckpt | 952MB | 2배 업스케일러 |
| ltx_2.3_spatial_upscaler_x1.5_f16.ckpt | 1.0GB | 1.5배 업스케일러 |

Gemma는 프롬프트를 임베딩으로 바꾸는 인코더이므로 생략 불가. 컨텍스트가 약 1,000토큰에서 잘리고 초과분은 조용히 버려짐 → 긴 프롬프트는 낭비.

---

## 생성 명령

```s
draw-things-cli generate \
  --model ltx_2.3_22b_distilled_1.1_i8x.ckpt \
  --prompt "a horse-drawn carriage on a tree-lined path, deep focus, photorealistic" \
  --negative-prompt "blurry, bokeh, shallow depth of field, distorted faces" \
  --width 1536 --height 1024 --frames 49 --steps 20 \
  --output clip.mov --video-format prores4444 \
  --disable-preview
```

image-to-video는 `--image`로 시작 프레임을 주고 `--strength`로 원본 유지 강도를 조절함.

```s
draw-things-cli generate --model ltx_2.3_22b_distilled_1.1_i8x.ckpt \
  --prompt "camera slowly pushes in" --image start.png --strength 0.35 \
  --width 1536 --height 1024 --frames 49 --output clip.mov
```

주요 인자는 다음과 같음.

| 인자 | 설명 |
|---|---|
| `--width`, `--height` | **64의 배수만 허용**. 위반 시 즉시 거부 |
| `--frames` | 8n+1 형태(49, 73, 97, 121, 153). 길이는 프레임수÷25 |
| `--steps` | 미지정 시 모델 권장값(distilled는 8+3 = 11스텝) |
| `--video-format` | prores4444, prores422hq, h264, hevc |
| `--config-json` | JSGenerationConfiguration 부분 오버라이드 |

864처럼 64로 나뉘지 않는 값을 넣으면 모델 로딩 전에 끊김.

```s
Error: Image dimensions must be multiples of 64, got 1536x864
```

---

## 스텝별 소요 시간

동일 조건에서 스텝만 바꾼 결과임.

| 해상도 | 11스텝 | 20스텝 | 30스텝 | 11→30 배율 |
|---|---|---|---|---|
| 1280×704 / 49프레임 | 7분31초 | 10분32초 | 12분42초 | 1.69배 |
| 1920×1088 / 49프레임 | 18분43초 | 23분44초 | 29분4초 | 1.55배 |

- 스텝 2.7배에 시간 1.6배 → 부선형
- 해상도가 높을수록 배율이 낮아짐(1.69 → 1.55) → VAE 디코드 고정비가 커서 샘플링 증분이 묻힘
- 같은 시간 예산이면 해상도보다 스텝에 배분하는 쪽이 유리

---

## 해상도별 소요 시간

49프레임·20스텝 고정 기준임.

| 해상도 | 픽셀 | 시간 |
|---|---|---|
| 1280×704 | 0.90M | 10분32초 |
| 1536×832 | 1.28M | 14분42초 |
| 1664×960 | 1.60M | 17분23초 |
| 1920×832 | 1.60M | 18분31초 |
| 1920×1088 | 2.09M | 23분44초 |

- 픽셀 2.32배에 시간 2.25배 → 거의 선형
- 1664×960과 1920×832는 픽셀이 같고 시간도 같음 → 비용은 화면비가 아니라 총 픽셀 수로 결정됨
- 시네마틱 2.3:1 화면비에 추가 비용 없음

---

## 길이별 소요 시간

1280×704·20스텝 고정 기준임.

| 프레임 | 길이 | 시간 | 프레임당 |
|---|---|---|---|
| 49 | 1.96초 | 10분32초 | 12.9초 |
| 73 | 2.92초 | 14분22초 | 11.8초 |
| 121 | 4.84초 | 23분44초 | 11.8초 |
| 153 | 6.12초 | 31분15초 | 12.3초 |

프레임당 비용이 12초 안팎으로 고정됨 → 길이도 선형.

---

## 메모리 한계는 프레임 수에서 옴

30편을 연속 생성하는 동안 스왑 증가량을 매 회차 기록함. 결과가 직관과 어긋남.

| 조합 | 픽셀×프레임 | 스왑 증가 | 압축 메모리 |
|---|---|---|---|
| 1920×1088 / 97프레임 | 203M | 0MB | 24.6GB |
| 768×512 / 377프레임 | 148M | +18,164MB | 37.3GB |

부하가 1.4배 적은 쪽이 스왑을 18GB 밀어냈음. macOS가 스왑 파일을 2GB에서 3GB로 확장할 정도였고, 그 구간에서 소요 시간이 예측치보다 23% 늘어남.

- 총 부하가 아니라 프레임 수 자체가 병목 → 어텐션 메모리가 프레임 축에서 먼저 터짐
- FHD로 4초를 뽑는 편이 480p로 15초를 뽑는 것보다 안전
- 300프레임 초과가 유일한 위험 구간

30편 전 회차의 스왑 증가는 0.0MB였음. 위험 구간은 이 배치 밖의 377프레임 시도에서만 나타남.

!!! warning
    프레임 수를 늘릴 때는 해상도를 올릴 때보다 훨씬 보수적으로 접근할 것.

---

## 열·전력

30편 10.3시간 연속 가동 중 온도를 추적함. sudo 없이 Apple Silicon 온도를 읽으려면 macmon을 씀(`powermetrics`는 root 권한 필요).

```s
brew install macmon
macmon pipe -s 1 | jq '{cpu: .temp.cpu_temp_avg, gpu: .temp.gpu_temp_avg, fan: .fans[0].rpm}'
```

| 지표 | 관측 범위 |
|---|---|
| CPU 온도 | 34~61°C |
| GPU 온도 | 34~67°C |
| 팬 | 1,320~1,335rpm (최대 3,500의 37~38%) |
| 전력 | 0~40W |

10시간 내내 GPU를 100% 물려도 67°C를 넘지 않고 팬은 38%에서 움직이지 않았음 → Mac Studio에서 열은 제약 조건이 아님.

---

## 제약 사항

| 항목 | 내용 |
|---|---|
| fps 조절 | 불가. `--fps` 인자가 없고 `--config-json '{"fps":24}'`는 오류 없이 무시됨. 출력은 항상 25fps |
| 해상도 | 64의 배수만. 1280×720, 1920×1080은 무효 → 1280×704, 1920×1088로 대체 |
| 최대 길이 | LTX-2.3 스펙상 20초(25fps·1080p). 다만 300프레임 초과는 스왑 위험 |
| 원경 인물 | 화면에서 20~30픽셀 높이로 잡히는 인물은 해상도를 올려도 뭉개짐. 프롬프트·스텝으로 해결 안 됨 |

프롬프트에 `shallow depth of field`를 넣으면 배경 인물이 설계대로 흐려짐. 배경까지 선명하게 뽑으려면 `deep focus`를 명시하고 네거티브 프롬프트로 `bokeh`, `shallow depth of field`를 눌러야 함.

---

## 권장 설정

| 목적 | 설정 | 소요 |
|---|---|---|
| 범용 | 1536×1024 / 49프레임 / 30스텝 | 20분 |
| 최고 화질 | 1920×1088 / 49프레임 / 30스텝 | 29분 |
| 시네마틱 | 1920×832 / 49프레임 / 30스텝 | 22분 |
| 빠른 초안 | 1280×704 / 49프레임 / 11스텝 | 7분 |
| 6초 컷 | 1280×768 / 153프레임 / 20스텝 | 31분 |

긴 영상은 한 번에 뽑지 말고 6초 이하 컷을 여러 개 만들어 편집으로 이을 것.

---

## 결론

M1 Max 64GB에서 FHD 2초 클립이 30스텝으로 메모리 스왑없이 29분에 나옴.

- 화질을 올리려면 해상도보다 스텝을 먼저 올릴 것
- 길이를 늘릴 때만 메모리를 경계할 것
- fps가 필요하면 생성이 아니라 후처리로 해결할 것
