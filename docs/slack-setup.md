# Slack App 설정 가이드

## 1. Slack App 생성

1. https://api.slack.com/apps → **Create New App** → **From scratch**
2. App Name: `Bootalk AI`
3. Workspace: 부톡 워크스페이스 선택

## 2. Socket Mode 활성화

1. **Settings > Socket Mode** → Enable
2. Token Name: `bootalk-socket` → Generate
3. `xapp-...` 토큰 복사 → `openclaw.json`의 `appToken`에 입력

## 3. Bot Token Scopes 추가

**OAuth & Permissions > Bot Token Scopes**에서 추가:

```
chat:write
channels:history
channels:read
groups:history
im:history
im:read
im:write
mpim:history
mpim:read
mpim:write
users:read
app_mentions:read
assistant:write
reactions:read
reactions:write
pins:read
pins:write
emoji:read
commands
files:read
files:write
```

## 4. Event Subscriptions 활성화

**Event Subscriptions** → Enable → **Subscribe to bot events**:

```
app_mention
message.channels
message.groups
message.im
message.mpim
reaction_added
reaction_removed
member_joined_channel
member_left_channel
channel_rename
pin_added
pin_removed
```

## 5. App Home 설정

**App Home** → **Messages Tab** 활성화 (DM 가능하게)

## 6. 워크스페이스에 설치

**Install App** → Install to Workspace → `xoxb-...` 토큰 복사 → `openclaw.json`의 `botToken`에 입력

## 7. 연결 확인

```bash
openclaw gateway
openclaw channels status --probe
```

Slack에서 `@Bootalk AI` 멘션하면 응답이 와야 합니다.
