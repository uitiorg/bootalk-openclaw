# OpenClaw Slash Commands (retired reference)

> 역사 기록입니다. 현재 Slack에서 이 OpenClaw slash command를 제공하는 runtime은 없습니다.

> Source: https://docs.openclaw.ai/tools/slash-commands

---

## 명령어 분류

### 세션 관리
| 명령어 | 설명 |
|--------|------|
| `/reset` | 현재 세션 초기화 |
| `/new [model]` | 새 세션 시작 (모델 선택 가능) |
| `/session idle` | 세션 유휴 처리 |
| `/session max-age` | 세션 최대 수명 설정 |

### 모델/상태
| 명령어 | 설명 |
|--------|------|
| `/model` | 모델 변경 |
| `/status` | 에이전트 상태 확인 |
| `/usage` | 사용량 조회 |
| `/whoami` | 현재 사용자/세션 정보 |

### 도구/컨텍스트
| 명령어 | 설명 |
|--------|------|
| `/tools` | 현재 세션에서 사용 가능한 도구 목록 |
| `/tools compact` | 간략 목록 |
| `/tools verbose` | 상세 목록 |
| `/context` | 현재 컨텍스트 확인 |
| `/btw` | 컨텍스트에 영향 없는 임시 질문 |

### 에이전트 제어
| 명령어 | 설명 |
|--------|------|
| `/subagents` | 서브에이전트 목록 |
| `/focus` | 특정 작업에 집중 |
| `/unfocus` | 집중 해제 |
| `/kill` | 에이전트 종료 |
| `/steer` | 에이전트 방향 조정 |

### Directives (단독 전송 시 세션에 지속 적용)
| 명령어 | 설명 |
|--------|------|
| `/think` | 사고 과정 활성화 |
| `/fast` | 빠른 응답 모드 |
| `/verbose` | 상세 출력 모드 |
| `/reasoning` | 추론 과정 표시 |
| `/elevated` | 상승된 권한 |
| `/exec` | 실행 허용 |

### 고급
| 명령어 | 설명 |
|--------|------|
| `/help` | 도움말 |
| `/commands` | 전체 명령어 목록 |
| `/plugins` | 플러그인 관리 |
| `/debug` | 디버그 모드 |
| `/config` | 설정 편집 |
| `/acp` | ACP 설정 |
| `/mcp` | MCP 서버 관리 |

---

## 설정

```json5
{
  channels: {
    slack: {
      commands: {
        native: true,          // Slack slash commands 활성화
        // name: "openclaw"   // 기본 슬래시 커맨드 이름
        // note: /status → /agentstatus (Slack이 /status 예약)
      }
    }
  }
}
```

---

## `/btw` — 임시 질문

컨텍스트 수정 없이 현재 세션 정보를 활용한 사이드 질문:
```
/btw 이 작업이 몇 분 걸릴 것 같아?
```
→ 답변이 대화 히스토리에 포함되지 않음.
