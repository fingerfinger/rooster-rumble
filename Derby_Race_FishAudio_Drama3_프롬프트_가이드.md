# ROOSTER RUMBLE: Fish Audio Drama 3 공식 규격 맞춤형 아나운서 프롬프트 가이드

- 기반 문서: [Fish Audio Drama 3 공식 문서 (docs.fish.audio)](https://docs.fish.audio/features/text-to-speech/drama-3)
- 핵심 원리:
  - 비표준 태그(`Style:`, `<tag>`)를 전면 배제하고, 공식 문서 표준인 **자연어 성우 연기 지시문(`[plain language direction]`)**과 **음향 이벤트 태그(`[pause]`)**로 전면 재구성
  - 실제 경마·스포츠 중계 전문 아나운서의 **성대 긁는 샤우팅, 숨 가쁜 호흡, 긴박한 템포**를 자연어 디렉팅으로 완벽 구현

---

## 1. Drama 3 공식 디렉팅 문법 원칙

1. **자연어 연기 지시문 (`[Plain language description]` 바로 뒤에 대사 배치)**:
   - Drama 3는 실제 스튜디오에서 성우에게 귓속말로 디렉팅하듯 대괄호 안에 감정, 속도, 호흡 상태를 영어 문장으로 적어줄 때 최상의 연기력을 발휘함.
   - 예시: `[screaming at the top of his lungs, breathless horse race caller] Down the stretch they come!`
2. **호흡 및 무음 제어 (`[pause]`)**:
   - 문장과 문장 사이에 `[pause]`를 명시하여, 파이썬 분할 도구가 오차 없이 감지할 수 있는 **0.4~0.6초 무음 구간**을 강제 형성.
3. **연결 억양 유도 (`[sharp rising intonation]`)**:
   - `[sharp rising intonation] Number 1,` 처럼 지시하여 번호 끝음이 자연스럽게 올라가 뒷문장과 물 흐르듯 이어지도록 발성 유도.

---

## 2. 5대 파트별 Drama 3 공식 표준 프롬프트 시트

---

### [파트 1] 단독 독립 샤우팅 멘트 (10종 일괄 생성)
- **저장 권장 파일명**: `batch_solo.mp3`
- **복사할 프롬프트**:

```text
[explosive energy, classic racetrack announcer shouting into a booming microphone] And away they go! [pause]

[high adrenaline, rapid-fire delivery, shouting with pure excitement] And they're off in Rooster Rumble! [pause]

[speaking fast, urgent and thrilling sports caller] Off the mark and away they sprint! [pause]

[sudden shock, gasping and shouting with alarm] Bad break! Stumbled off the line! [pause]

[concerned, urgent commentary, speaking rapidly] Awkward start! Losing ground early! [pause]

[screaming at the top of his lungs, electrifying stadium roar, final stretch hype] Down the stretch they come! [pause]

[breathless, hyper-fast cadence, roaring with intense adrenaline] They're sprinting for the wire! [pause]

[frantic shouting, voice cracking with extreme tension, out of breath] Too close to call! They cross the line together! [pause]

[hysterical screaming, absolute climax, desperate photo finish call] Nose to nose at the wire! Who took it?! [pause]

[triumphant, booming baritone roar, stadium champion announcement] It is all victory at the wire!
```

---

### [파트 2] 연결 세트 1: 초반 선두 경쟁 3종 (번호 + 선두 콜)
- **저장 권장 파일명**: `batch_early.mp3`
- **복사할 프롬프트**:

```text
[sharp rising intonation, live racetrack call] Number 1, [speaking very fast, thrilling excitement] showing blazing speed to take the lead! [pause]

[sharp rising tone, fast delivery] Number 2, [punchy, commanding sports commentary] grabs the lead early on! [pause]

[sharp rising tone, loud projection] Number 3, [high energy, confident tempo] setting the pace out front!
```

---

### [파트 3] 연결 세트 2: 중반 역전 & 접전 4종
- **저장 권장 파일명**: `batch_overtake.mp3`
- **복사할 프롬프트**:

```text
[sharp rising intonation, shocked and breathless] Number 4, [screaming with sudden surprise] takes over the lead! [pause]

[sharp rising tone, intense anticipation] Number 5, [explosive power, roaring sports caller] makes a powerful surge! [pause]

[sharp rising tone, rapid-fire pacing] Number 6, [frantic screaming, intense momentum] surging to the front! [pause]

[sharp rising tone, breathless] Number 1 and Number 2, [screaming violently at maximum intensity, thrilling clash] head-to-head in a fierce battle!
```

---

### [파트 4] 연결 세트 3: 종반 직선주로 스퍼트 2종
- **저장 권장 파일명**: `batch_stretch.mp3`
- **복사할 프롬프트**:

```text
[sharp rising tone, roaring near the finish line] Number 5, [screaming at maximum intensity, out of breath] leading them all the way to the wire! [pause]

[sharp rising tone, frantic and electrifying] Number 3, [shouting with pure adrenaline, thunderous voice] charging hard from behind!
```

---

### [파트 5] 연결 세트 4: 골인 및 최종 우승 2종
- **저장 권장 파일명**: `batch_win.mp3`
- **복사할 프롬프트**:

```text
[sharp rising tone, historic championship roar] Number 5, [screaming in utter ecstasy and awe, cracking voice] wins it wire-to-wire! Unbelievable! [pause]

[sharp rising tone, booming victory cry] Number 3, [triumphant roar echoing across the grandstand] takes the victory in Rooster Rumble!
```

---

## 3. 웹 UI 및 API 활용 가이드

### 1) Fish Audio 웹 인터페이스 사용 시
- 웹 에디터 모델 선택에서 **`Drama 3`** 확인.
- 위 코드 블록을 그대로 복사하여 텍스트 창에 입력 후 생성 및 다운로드.
- 파일을 `assets/audio/race/voice_import/` 폴더에 넣고 분할 명령어 실행.

### 2) Fish Audio API 사용 시 (참고 사양)
- 엔드포인트: `POST https://api.fish.audio/v1/tts`
- 헤더: `model: drama-3`, `Authorization: Bearer <API_KEY>`
- 요청 페이로드:
  ```json
  {
    "text": "[screaming at the top of his lungs] Down the stretch they come! [pause]",
    "format": "mp3"
  }
  ```
