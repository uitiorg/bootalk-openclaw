# Bootalk 서비스 아키텍처 & 팀 현황 (historical snapshot)

> 보존용 문서입니다. 서비스·팀·인프라 정보는 2026-04 기준이며 현재 상태를 의미하지 않습니다. 현재 운영 구조는 [`../AGENTS.md`](../AGENTS.md)를 참고하세요.

> 출처: uitiorg/team-discussions#75 (2026-02-06 기준)
> 팀 작업 현황: 2026-04-02 기준 GitHub 활동 분석

---

## 서비스 개요

**Bootalk(부톡)** — 부동산 중개 플랫폼. 아파트/오피스텔/상가 매물 검색, 중개사 매칭, AI 검색, 실시간 채팅.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 웹 프론트엔드 | Next.js 16, React 19, styled-components, Zustand, Tanstack Query |
| 앱 | Expo SDK 54, React Native 0.81.5, React Navigation 6 |
| 공통 | TypeScript, pnpm + Turborepo, Sentry, AWS Amplify v6 |
| 백엔드 | Spring Boot 3.1.1, Kotlin 1.8.22, Java 17 |
| 데이터 | MySQL (JPA + QueryDSL), Redis, Elasticsearch, Manticore Search |
| 메시징 | AWS SNS/SQS, Spring Event |
| 인증 | AWS Cognito + JWT |
| 인프라 | GCP GKE + AWS (RDS, S3, CloudFront, ECR, SNS/SQS) |
| 모니터링 | Grafana + Prometheus + Loki + Tempo + OpenTelemetry |
| CI/CD | GitHub Actions (self-hosted macOS) + Jenkins + ArgoCD |

---

## 핵심 레포

### 활성 서비스

| 레포 | 역할 | 상태 |
|------|------|------|
| `uitiorg/btalk2.1_backend` | MSA 백엔드 모노레포 (Spring Boot/Kotlin) | 활발 |
| `uitiorg/frontend-monorepo` | 웹(Next.js) + 앱(Expo) + 어드민 모노레포 | 활발 |
| `uitiorg/legacy-service` | 레거시 Java Servlet 서버 (MSA 전환 중) | 활발 |
| `uitiorg/bootalk-amplify` | AWS Amplify (채팅/인증) | 활발 |
| `uitiorg/manifest-ops` | K8s 매니페스트 GitOps | 활발 |
| `uitiorg/bootalk-infra` | 인프라 IaC | 활발 |
| `uitiorg/ubuntu-crawler` | DB 데이터 크롤러 + 프로시저 | 활발 |

### MSA 서비스 목록 (btalk2.1_backend)

| 서비스 | 경로 | 역할 |
|--------|------|------|
| apart-service | `/apartments` | 아파트 매물 |
| ai-service | `/ais` | AI 검색 |
| user-service | `/users` | 사용자 인증 |
| chat-service | `/chats` | 실시간 채팅 |
| agent-service | — | 중개사 |
| notification-service | — | 알림 (알림톡) |
| match-service | `/matches` | 매물 매칭 |
| real-price-service | `/real-prices` | 실거래가 |
| community-service | `/communities` | 커뮤니티 |
| data-service | `/data` | 데이터 (MyBatis) |
| office-store-service | `/office-stores` | 공유오피스 |
| event-service | — | 이벤트/캐시 |
| batch-service | — | 배치 작업 |
| legacy-service | `/legacies` | 레거시 프록시 |

---

## 인프라 / 엔드포인트

| 환경 | API | 웹 | 어드민 |
|------|-----|-----|--------|
| 개발 | `api-dev.bootalk.co.kr` | `dev.bootalk.co.kr` | `bics-dev.bootalk.co.kr` |
| 운영 | `api.bootalk.co.kr` | `bootalk.co.kr` | `bics.bootalk.co.kr` |

- **DB 개발**: GCP Cloud SQL `34.22.66.66`
- **DB 운영**: AWS RDS `btalk.c51hdr3yu7wk.ap-northeast-2.rds.amazonaws.com`
- **CDN**: CloudFront `d1ow1zydcbqtx3.cloudfront.net`
- **Grafana 운영**: `metrics.bootalk.co.kr/grafana`

---

## 팀원 작업 현황 (2026-04-02~03 기준)

### 주우철 (juuc, CDO) — 프론트엔드 + 인프라

**진행 중인 작업:**
- **Synthetic Monitoring 구축**: Blackbox Exporter + k6 CronJob → EKS prod 배포, ArgoCD 앱 추가 (PR open)
  - `manifest-ops#45` merged, `bootalk-infra#42` open
- **App v3.5.26 릴리즈**: release PR open, develop → release/v3.5.x 머지 진행 중
  - `frontend-monorepo#1128`, `#1129` open

**최근 완료:**
- `fix(app)`: KAKAO_50 유저 라우팅 오류 수정 (CompanyPlusEvent)
- `refactor(app)`: bottom modal 28개 파일 통합 완료
- `fix(all)`: 대표 평형 autofill MSA API 전환
- `fix`: Manticore 검색 인덱스에서 soft-delete 아파트 제외
- `feat`: real-price 데이터 신선도 synthetic monitoring 추가 (btalk2.1_backend#546)
- semugpt 서면질의 UI 개선

**오픈 이슈:**
- `frontend-monorepo#1132`: SafeAreaView per-screen 마이그레이션 (refactor)
- `frontend-monorepo#1130`: 401/network 에러 필터링 (PR open)

---

### 정정일 (12OneTwo12, Dev) — 백엔드 + MSA 전환

**현재 메인 작업: 레거시 Protocol → MSA 전환** (아파트 상세 관련 API 전면 교체 중)

| 작업 | 상태 | PR |
|------|------|-----|
| Protocol 206 (대표 평형 조회) → MSA | ✅ 완료 | `frontend-monorepo#1137`, `btalk2.1_backend#549` |
| Kovi/네이버 평면도 → 자체 plan-images API | ✅ 완료 | `frontend-monorepo#1138` |
| Protocol 302, 10212, 10213 (평형 목록) → MSA | ✅ 완료 | `frontend-monorepo#1140`, `btalk2.1_backend#549` |
| Protocol 1110 (지도 좌표 검색) → MSA | ✅ 완료 | `frontend-monorepo#1143`, `btalk2.1_backend#551` |
| 아파트 실거래가/차트 레거시 → MSA | 🔄 진행 중 | `btalk2.1_backend#552` open |

**최근 버그 수정:**
- `fix`: 클러스터 응답 가격 10배 오차 (대표 평형 dedup 누락) → `btalk2.1_backend#553` merged
- `fix`: 지도 좌표 검색 API 대표 평형 dedup + 최소 세대수 필터 → `btalk2.1_backend#551`
- `fix`: 랭킹 조회 completion null NPE → `btalk2.1_backend#544`

**오픈 이슈:**
- `ubuntu-crawler#48`: `apt_deal` 2026년 3월+ 행의 join_key format regression (18자리 bjdCode) → 전체 SP JOIN 깨짐 (🔴 버그)
- `ubuntu-crawler#46`: `apt_supply_pyeong` 관련 프로시저 인덱스 누락 + non-sargable 조건 개선
- `btalk2.1_backend#547`: AIPropertyFinderResult N+1 API calls — Batch endpoint 필요 (performance)

---

## 현재 주요 흐름

1. **레거시 Protocol → MSA 전환** (정정일 주도): 아파트 상세 페이지 관련 레거시 API를 MSA로 전면 교체 중. frontend + backend 동시 PR.
2. **Synthetic Monitoring 구축** (주우철): Blackbox Exporter + k6로 운영 API 헬스 체크 자동화.
3. **앱 v3.5.26 릴리즈** (주우철): bottom modal 통합, 집 내놓기 리뉴얼, design token 적용.
4. **DB 정합성 이슈** (정정일): ubuntu-crawler에서 2026-03 이후 join_key format 변경으로 SP JOIN 전면 깨짐.
