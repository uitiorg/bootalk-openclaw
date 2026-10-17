# btalk2.1_backend 서비스 인증

Bootalk 스크립트나 Codex task가 내부 API를 읽어야 할 때 사용하는 서비스 인증 참고자료입니다. 이 문서는 현재 API가 실제로 배포되어 있다는 증거가 아니며, backend endpoint와 secret 주입이 준비된 환경에서만 적용합니다.

## 요청 흐름

```text
자동화 또는 직접 실행 스크립트
  │
  ├─ POST /internal/auth/service-token
  │    X-Internal-Api-Key: ${BOOTALK_API_KEY}
  │
  └─ GET /api/any-endpoint
       Authorization: Bearer ${SERVICE_TOKEN}
```

서비스 토큰은 짧은 수명의 인증 토큰이어야 하며, 출력·로그·automation memory에 저장하지 않습니다.

## Backend prerequisite

`btalk2.1_backend`에 아래 endpoint와 설정을 별도로 구현·배포해야 합니다.

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
        val token = jwtTokenProvider.createServiceToken("bootalk-automation")
        return ApiResponse.success(TokenResponse(accessToken = token))
    }
}
```

```yaml
btalk:
  internal:
    api-key: ${INTERNAL_API_KEY}
```

배포 전에는 endpoint의 인증 예외 처리, rate limit, audit log, 환경별 key 분리를 backend 소유자가 확인해야 합니다.

## Client environment

현재 repo의 관련 skill은 다음 환경변수를 사용합니다.

```text
BOOTALK_API_URL=https://api.bootalk.com
BOOTALK_API_KEY=<injected outside the repository>
```

Codex automation에서는 automation secret store 또는 실행 환경에서 주입하고, prompt·memory·Slack 보고에 값을 남기지 않습니다. local CLI에서는 shell 환경변수로만 주입합니다.

## Verification checklist

- 대상 환경이 PROD인지 DEV인지 확인
- endpoint가 실제로 배포되어 있는지 확인
- read-only 조회인지 확인
- HTTP status와 응답 schema를 확인
- token이나 API key가 로그에 노출되지 않았는지 확인
