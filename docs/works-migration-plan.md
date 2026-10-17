# WORKS → Slack 게시판 마이그레이션 플랜

> Historical migration plan. 아래 명령은 2026년 WORKS → Slack 이전 당시의 기록이며, 현재 Slack live state와 실행 주체를 의미하지 않습니다. 새 채널·Canvas 작업 전 Slack connector로 대상을 재확인하세요.

> 수집일: 2026-03-31 | 총 57개 게시글 | 10개 카테고리

---

## 마이그레이션 전략

게시글 유형별 Slack 형식 매핑:

| 유형 | Slack 형식 | 기준 |
|------|-----------|------|
| 항상 보이는 규칙/정책 | 📄 **Canvas** | 수시로 참조하는 내부 규정/가이드 |
| 중요 공지 | 📌 **Pin** | 일회성이나 중요한 공지 |
| 외부 링크 모음 | 🔖 **Bookmark** | 주로 Google Docs/Sheets/Drive 링크 |
| 아카이브 기록 | 💬 **Message** | 과거 기록 보존, 업무 변경 등 |

---

## Phase 1: 채널 생성

현재 존재하는 채널: `#공지사항` `#dev` `#marketing` `#cs` `#brokerage` `#온보딩`

**새로 만들어야 할 채널:**

```bash
BOT_TOKEN="${SLACK_BOT_TOKEN}"

# 회사내규 (공개)
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/conversations.create \
  -d '{"name":"회사내규","is_private":false}'

# 업무규칙 (공개)
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/conversations.create \
  -d '{"name":"업무규칙","is_private":false}'

# design (공개)
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/conversations.create \
  -d '{"name":"design","is_private":false}'

# admin (비공개)
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/conversations.create \
  -d '{"name":"admin","is_private":true}'
```

---

## Phase 2: 채널별 마이그레이션 상세

---

### `#회사내규` — 회사 내규 / 이념 (2개)

**→ Canvas 1개로 통합 (두 게시글 모두 영구 참조 문서)**

**Canvas 제목:** "부톡 핵심 가치 & 철학"

```
## 10 Career Principles in 부톡
_이훈구 | 2024.10.23_

1. 적당히~ 대충~ 은 없다.
고객(사용자)은 최고-최적에만 돈을 쓴다...

2. 고객 & 상황
문제를 해결할 때, 고객과 고객이 처한 상황을 먼저 생각하자...

[이하 10개 원칙 전문]

---

## 업무에서의 설득의 중요성
_이훈구 | 2024.09.13_

성공하는 사람은 본인의 '말'과 '글', '그림' 등, '콘텐츠'로 상대를 '설득'해서 내가 의도한 대로 생각하거나 행동하게 만드는 사람이다...
```

**실행:** Canvas는 Slack 웹 UI에서 직접 생성 후 내용 붙여넣기 (API 미지원)

---

### `#업무규칙` — 업무 규칙 (9개)

**포맷 결정:**

| 게시글 | 형식 | 이유 |
|--------|------|------|
| 업무 메신저 규칙 | 📄 Canvas | 수시 참조, 단 내용을 "Slack"으로 업데이트 필요 |
| 구글드라이브 개인 폴더 활용 규칙 | 📄 Canvas | 항상 참조하는 파일 규칙 |
| 부톡 비즈니스 이메일 규칙 | 📄 Canvas | 항상 참조 |
| 주간업무일지 사용법 | 📄 Canvas | 참조 |
| 결제 신청 프로세스 | 📄 Canvas | 항상 참조하는 프로세스 |
| 연차 안내 | 📄 Canvas | 항상 참조 |
| [공지] 취업규칙 (PDF) | 🔖 Bookmark | 파일 링크 |
| JIRA 작성 방법 | 📌 Pin in `#dev` | 개발팀 전용 → `#dev`로 이동 |
| 웍스 할 일(To DO) 사용 | 💬 Message | Slack으로 전환되면 불필요 (아카이브) |

**Canvas 구성 (하나의 Canvas에 섹션별로 통합):**

```markdown
# 부톡 업무 규칙

## Slack 메신저 규칙
[업무 메신저 규칙 내용, "네이버웍스" → "Slack"으로 업데이트]

## 구글드라이브 파일 관리 규칙
[구글드라이브 개인 폴더 활용 내용]

## 비즈니스 이메일 규칙
[부톡 비즈니스 이메일 규칙 내용]

## 주간업무일지 사용법
[주간업무일지 사용법 내용]

## 결제 신청 프로세스
[결제 신청 프로세스 내용]

## 연차 규정
[연차 안내 내용]
```

**주의:** "업무 메신저 규칙" 내 "네이버웍스 → Slack" 내용 변경 필요

**Bookmark 추가:**
```bash
# 취업규칙 PDF 링크 (bookmark)
# 채널 ID는 생성 후 확인 필요
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/bookmarks.add \
  -d '{"channel_id":"<#업무규칙 채널ID>","title":"부톡(주) 취업규칙","type":"link","link":"<PDF URL>"}'
```

---

### `#공지사항` — 공지사항 (6개)

| 게시글 | 형식 | 내용 |
|--------|------|------|
| 업무 시간 규칙 | 📄 Canvas | 영구 참조 (→ `#업무규칙` Canvas에 통합 가능) |
| 2025년도 부톡 목표 | 📌 Pin | 중요 공지 |
| 간식 신청 방법 | 📄 Canvas 섹션 + 🔖 Bookmark | 매월 반복 참조 |
| 팀원 연락처 / 회사 계정 목록 | 🔖 Bookmark | Google Sheet 링크 |
| 탕비업무 배분 관련 | 🔖 Bookmark | Google Sheet 링크 |
| 네이버 SEO 바로가기 올리기 작업 | 💬 Message | 일회성 태스크 (아카이브) |

**Canvas "공지사항 필수 정보":**
```markdown
# 공지사항 필수 정보

## 업무 시간
- 자율 출근: 09:30~10:30 중 선택 (월 1회 변경)
- 점심: 12:30~13:30
- 전체 업무시간: 09:30~19:30

## 간식 신청
- 매월 15일 (15일이 평일이 아니면 조정)
- 인당 3만원 이하 (배송비 포함)
- 신청 시트: [링크]

## 팀원 연락처 & 계정: [Google Sheet 링크]
## 탕비업무 배분: [Google Sheet 링크]
```

**메시지 (Pin):**
```bash
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/chat.postMessage \
  -d '{
    "channel": "C0APYE86NAW",
    "text": "📋 *2025년도 부톡 목표 / 경쟁력 / 서비스 과제*\n\n모두 잘 읽어주시고, 궁금한 사항 질문 있으시면 꼭 해주세요!\n\n• 2025 기술 개발 목표: [Google Docs 링크]\n• 2025년 1/4분기 PLAN: [Google Slides 링크]",
    "username": "부톡봇"
  }'
```

---

### `#온보딩` — 신규 입사자 OT (1개)

**→ Canvas 1개 (온보딩 가이드)**

```markdown
# 부톡 신규 입사자 온보딩 가이드
_전유진 | 2025.03.04_

부톡에 합류하신 것을 환영합니다! 🎉

## 체크리스트

### 계정 설정
- [ ] Google 계정 (사내 계정: OOO@bootalk.co.kr)
- [ ] Slack 가입 및 채널 참여
- [ ] JIRA 계정 (개발팀)
- [ ] Naver WORKS 계정 (→ Slack으로 전환됨)

### 필수 문서 확인
- 부톡 온보딩 가이드북: [Google Docs 링크]
- 업무 규칙: #업무규칙 채널 Canvas 참조
- 회사 내규: #회사내규 채널 Canvas 참조
- 팀원 연락처: #공지사항 채널 Bookmark 참조

### 서비스 로그인
- 모든 서비스 로그인은 구글 계정 사용
```

---

### `#dev` — DEV / DATA (12개)

| 게시글 | 형식 | 비고 |
|--------|------|------|
| 앱 테스트 방법 | 📌 Pin | 개발자 필수 참조 |
| 부톡 데이터 R&R | 📄 Canvas | 역할 정의 (영구 참조) |
| 부톡 기술 문서/DB 문서화 가이드 | 📌 Pin | 진행 중인 작업 |
| 부톡 SEO / OG | 📄 Canvas | 기술 참조 문서 |
| 농협 관련 문서 | 📄 Canvas | 기술 참조 (GitHub 링크 등) |
| 부톡 아파트/사무실 매물 추천 알고리즘 | 🔖 Bookmark | Google Docs 링크 |
| 부톡/농협 서비스 지역 및 크롤링 범위 | 🔖 Bookmark | Google Sheet 링크 |
| 데이터팀 업무 목록 | 🔖 Bookmark | Google Sheet 링크 |
| 부톡 TTA 성능시험성적서 | 🔖 Bookmark | 파일 링크 |
| 아파트 상세페이지 `매물 추이` | 💬 Message | 알고리즘 설명 (아카이브) |
| [아이디어] 직거래 편향적 중개거래 | 💬 Message | 아이디어 기록 |
| 부톡 아파트 추가 업데이트 안내 | 💬 Message | 2023년 공지 (아카이브) |

**Canvas "개발팀 핵심 문서":**
```markdown
# 개발팀 핵심 참조

## 데이터 R&R (주우철)
- 아파트 실거래가 수집, 아파트 기본정보, 중개사무소 정보 등 8개 도메인 담당
[전체 R&R 내용]

## SEO / OG 가이드
[부톡 SEO/OG 전문]

## 농협 프로젝트 문서
- API 서버: https://github.com/seokjeatuiti/nonghyup-kok-springboot
- 배치 서버: https://github.com/seokjeatuiti/nonghyup_batch
```

**메시지 (Pin) - 앱 테스트 방법:**
```bash
curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
  https://slack.com/api/chat.postMessage \
  -d '{
    "channel": "C0APYE7MLEN",
    "text": "📱 *앱 테스트 방법*\n\n1. expo 권한 요청 (개발팀에 문의)\n2. expo 링크에서 \"development\" 빌드 설치\n3. 우상단 프로필 → 사내 계정 로그인\n4. Updates → 최신 버전 Open\n\n*테스트 계정:*\n• OTP: 항상 123456\n• 중개사 ID/PW: 013 3333 3333 / 33333333\n• BICS dev: bics-dev.bootalk.co.kr\n• 부톡 웹 dev: dev.bootalk.co.kr",
    "username": "부톡봇"
  }'
```

---

### `#brokerage` — BROKERAGE (7개)

| 게시글 | 형식 | 비고 |
|--------|------|------|
| BICS 중개사 계정 생성 프로세스 | 📄 Canvas | 핵심 운영 프로세스 |
| 파트너 부동산 가입 프로세스 | 📄 Canvas | 핵심 운영 프로세스 |
| 중개사 계정 등록 과정 | 📄 Canvas | 운영 가이드 |
| 중개사 이관 시 주의사항 | 📄 Canvas | 운영 가이드 |
| 중개사 가입 신청 명단 및 프로세스 | 🔖 Bookmark | 시트 링크 |
| 중개사 퍼포먼스 관리 문서 | 🔖 Bookmark | Google Docs 링크 |
| 중개수수료 규정 | 🔖 Bookmark | 첨부파일 (PDF) |
| 중개사 평가 및 관리 | 🔖 Bookmark | Google Sheet 링크 |

**Canvas "중개사 운영 가이드" (4개 프로세스 통합):**
```markdown
# 중개사 운영 가이드

## 1. 신규 중개사 계정 생성 프로세스 (BICS)
1. 프로필 사진 & 자격증 파일 전달 (유진 → 찬경)
2. 마스킹 및 프로필 이미지 생성 (찬경) → 구글 드라이브 업로드
3. 구글 드라이브에서 중개사 정보 확인 (샛별) → 시트 작성
4. BICS 계정 생성 (샛별)
5. 지역 배정 (현석/민석 또는 중개팀)
6. 중개사 퇴사/탈퇴 처리: BICS 계정 클로징 + 고객 이관

## 2. 파트너 부동산 가입 프로세스
1. 카카오톡 채널 상담 접수 → 전화 예정 안내
2. 전화 상담 (훈구): 가입 및 지역 상담
3. 지역 판단 (현석)
4. 인보이스 작성 및 발송 (유진)
5. 아이디 및 사용법 전달 (민석): 월이용료 입금 확인 후

## 3. 중개사 이관 시 주의사항
Case 1. 지역 담당 중개사 교체:
1. 새 중개사(A)에게 기존 매칭 고객 여부 확인
2. 중복 시 대화 내용 전달
3. 고객에게 재신청 요청 후 기존 대화창 삭제

## 4. 중개사 가입 신청 프로세스
[상세 7단계 프로세스]
```

---

### `#marketing` — MARKETING / SALES (11개)

| 게시글 | 형식 | 비고 |
|--------|------|------|
| 부톡 단지 링크 공유하기 | 📄 Canvas | 업무 가이드 |
| 네이버 성과형 디스플레이 광고 숙지사항 | 📄 Canvas | 참조 문서 |
| 부톡 이벤트 가이드 라인 | 🔖 Bookmark | 파일 링크 |
| 부톡 내 광고 상품 소개서 (2025.08) | 🔖 Bookmark | 파일 링크 |
| 부톡 내 광고 상품 소개서 | 🔖 Bookmark | 구버전 |
| 부톡 시연 영상 목록 시트 | 🔖 Bookmark | Google Sheet |
| 부톡(주) 중소기업확인서 | 🔖 Bookmark | 파일 |
| [구글 애즈] 문구, 이미지 영상 모음 | 🔖 Bookmark | 파일 |
| 아파트 & 오피스텔 등기 시장 규모 | 💬 Message | 리서치 기록 |
| 서울시 상업/업무용 부동산 시장 규모 | 💬 Message | 리서치 기록 |
| 수도권 아파트 시장규모 재산출 | 💬 Message | 리서치 기록 |

---

### `#cs` — CUSTOMER SERVICE (0개)

게시글 없음. 채널만 유지.

---

### `#design` — DESIGN (1개)

| 게시글 | 형식 | 비고 |
|--------|------|------|
| 우수부동산서비스 사업자 인증서, 연계사업자 확인서 | 💬 Message | 파일 링크 공지 |

---

### `#admin` (Private) — ADMIN (7개)

| 게시글 | 형식 | 비고 |
|--------|------|------|
| 대표이사 중임 신청서류 | 📄 Canvas | 법인 필수 서류 절차 |
| 등기, 주주총회 관련 | 💬 Message | 아카이브 |
| 구글 클라우드 프로젝트(GCP) 크레딧 수령 | 💬 Message | 참조 |
| 2025 위치정보사업자 정기점검 | 💬 Message | 참조 |
| 신규 사업 정리 | 🔖 Bookmark | Google Sheet |
| 표준투자계약서 | 🔖 Bookmark | 외부 링크 |
| 주요 파일 공유 | 🔖 Bookmark | Google Drive 링크 |

---

## Phase 3: 실행 스크립트

### 아카이브 메시지 일괄 전송

아카이브용 메시지(💬)는 스크립트로 일괄 전송 가능:

```bash
#!/bin/bash
BOT_TOKEN="${SLACK_BOT_TOKEN}"

post_message() {
  local channel=$1
  local text=$2
  curl -s -X POST -H "Authorization: Bearer $BOT_TOKEN" -H "Content-Type: application/json" \
    https://slack.com/api/chat.postMessage \
    -d "{\"channel\":\"$channel\",\"text\":\"$text\",\"username\":\"부톡봇\"}" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('ok') else d.get('error'))"
}

# === #dev 아카이브 메시지 ===
post_message "C0APYE7MLEN" "📦 *[WORKS 아카이브] 아파트 상세페이지 매물 추이 알고리즘*
_박석제 | 2025.05.14_

특정 아파트의 거래 활발성 지수 계산 알고리즘:
1. 월별 대표 매물 선정 (가장 최근 등록 기준)
2. 실제 거래량 파악
3. 거래 활발성 = 실제 거래수 / 매물수 (예: 2/10 = 20%)
4. 내림차순 시각화"

# [추가 메시지들...]
```

---

## Phase 4: 마이그레이션 체크리스트

### 채널 생성
- [ ] `#회사내규` 생성
- [ ] `#업무규칙` 생성
- [ ] `#design` 생성
- [ ] `#admin` (private) 생성
- [ ] 팀원 초대 (각 채널에 맞는 멤버)

### Canvas 생성 (수동 - Slack UI에서)
- [ ] `#회사내규` — "부톡 핵심 가치 & 철학" (2개 게시글 통합)
- [ ] `#업무규칙` — "부톡 업무 규칙" (6개 게시글 통합, 메신저 규칙 내용 Slack으로 업데이트)
- [ ] `#공지사항` — "공지사항 필수 정보" (간식/연락처/탕비업무)
- [ ] `#온보딩` — "신규 입사자 온보딩 가이드"
- [ ] `#dev` — "개발팀 핵심 참조" (R&R, SEO/OG, 농협)
- [ ] `#brokerage` — "중개사 운영 가이드" (4개 프로세스 통합)
- [ ] `#marketing` — "마케팅 참조 문서" (링크 공유 가이드 + 광고 숙지사항)
- [ ] `#admin` — "대표이사 중임 신청서류"

### Bookmark 추가 (채널 상단)
- [ ] `#업무규칙` — 취업규칙 PDF
- [ ] `#공지사항` — 팀원 연락처 Sheet, 탕비업무 Sheet
- [ ] `#dev` — 알고리즘 Docs, 데이터팀 업무 목록, 크롤링 범위
- [ ] `#brokerage` — 가입 신청 명단, 퍼포먼스 관리, 수수료 규정, 평가 관리
- [ ] `#marketing` — 이벤트 가이드, 광고 소개서, 시연 영상, 중소기업확인서
- [ ] `#admin` — 신규 사업 정리, 투자계약서, 주요 파일 공유

### 메시지 전송 (스크립트)
- [ ] `#dev` 아카이브 4개 (매물추이, 아이디어, TTA, 아파트 추가 업데이트)
- [ ] `#marketing` 아카이브 3개 (시장규모 리서치)
- [ ] `#공지사항` 아카이브 1개 (네이버 SEO 작업)
- [ ] `#design` 메시지 1개 (인증서)
- [ ] `#admin` 아카이브 4개

### 핀 등록
- [ ] `#dev` — 앱 테스트 방법
- [ ] `#dev` — DB 문서화 가이드
- [ ] `#공지사항` — 2025 부톡 목표
- [ ] `#업무규칙` — JIRA 작성 방법

---

## 주의사항

1. **내용 업데이트 필요:** "업무 메신저 규칙" 내 "네이버 웍스" → "Slack", "할 일" → "JIRA/Slack" 등 도구명 변경
2. **파일 접근:** Google Docs/Drive 링크는 팀원 계정에 공유 상태인지 확인
3. **ADMIN 채널:** Private 채널이므로 대표, 특정 멤버만 초대
4. **Canvas 한계:** Bot API로 Canvas 생성 불가 (bookmarks:write 스코프 없음) → Slack UI에서 수동 생성
5. **메신저 규칙 내용 업데이트:** WORKS 전환 전에 메신저 규칙을 Slack 기준으로 새로 작성 권장

---

## 관련 파일

- 전체 게시글 원문: [GitHub Gist](https://gist.github.com/juuc/f50d631ee2475e9419fe01a0ed19ebf1) (`works-board-posts.md`)
- Slack 채널 매핑: 동일 Gist (`slack-vs-works.md`)
