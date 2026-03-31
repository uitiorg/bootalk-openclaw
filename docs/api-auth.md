# btalk2.1_backend 인증 방법

## 구조

```
OpenClaw Skill (curl)
  │
  ├─① POST /internal/auth/service-token
  │    Header: X-Internal-Api-Key: {secret}
  │    Response: { data: { accessToken: "eyJ..." } }
  │
  └─② GET /api/any-endpoint
       Header: Authorization: Bearer {accessToken}
       → 기존 JwtAuthenticationFilter가 검증
       → UserRole.SERVICE로 인식
```

## 사전 작업 (백엔드에서 1회)

`btalk2.1_backend`에 파일 1개 + 설정 1줄 추가 필요:

### 1. InternalAuthController.kt

```kotlin
@RestController
@RequestMapping("/internal/auth")
class InternalAuthController(
    private val jwtTokenProvider: JwtTokenProvider,
    @Value("\${btalk.internal.api-key}") private val internalApiKey: String,
) {
    @Public
    @PostMapping("/service-token")
    fun issueServiceToken(
        @RequestHeader("X-Internal-Api-Key") apiKey: String,
    ): ApiResponse<TokenResponse> {
        if (apiKey != internalApiKey) {
            throw AuthenticationException("Invalid API key")
        }
        val token = jwtTokenProvider.createServiceToken("openclaw-bot")
        return ApiResponse.success(TokenResponse(accessToken = token))
    }
}
```

### 2. application.yml

```yaml
btalk:
  internal:
    api-key: ${INTERNAL_API_KEY}
```

## OpenClaw 설정

`~/.openclaw/openclaw.json`의 skills entries에 환경변수 추가:

```json5
{
  skills: {
    entries: {
      "bootalk-properties": {
        env: {
          BOOTALK_API_URL: "https://api.bootalk.com",
          BOOTALK_API_KEY: "your-internal-api-key",
        },
      },
    },
  },
}
```
