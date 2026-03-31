/**
 * Sentry webhook transform for OpenClaw.
 *
 * Receives Sentry webhook payloads and generates triage prompts.
 * Delivery target is configured via SENTRY_DELIVERY_CHANNEL and SENTRY_DELIVERY_TARGET
 * environment variables (defaults to Slack #sentry-alerts).
 *
 * Architecture:
 *   Sentry.io → Cloudflare Tunnel → OpenClaw Sentry Gateway (port 19789)
 *   → this transform → triage agent → delivery to Slack/Telegram
 */

const DELIVERY_CHANNEL = process.env.SENTRY_DELIVERY_CHANNEL || "slack";
const DELIVERY_TARGET = process.env.SENTRY_DELIVERY_TARGET || "slack:#sentry-alerts";

// Fallback for Telegram (legacy):
// SENTRY_DELIVERY_CHANNEL=telegram
// SENTRY_DELIVERY_TARGET=telegram:-5152975056

export default function transform(ctx) {
  const payload = ctx.payload || {};
  const action = payload.action || "unknown";
  const data = payload.data || {};
  const event = data.event || {};

  const issueId =
    event.issue_id || data.issue?.id || payload.issue_id || payload.issueId || "";
  const shortId = data.issue?.short_id || event.issue || "";
  const title = event.title || event.metadata?.value || "";
  const culprit = event.culprit || event.location || "";
  const level = event.level || "";
  const project = event.project || data.project || "";
  const issueUrl = event.issue_url || event.web_url || event.url || "";

  // 1) test ping: always silent
  if (action === "test") {
    return {
      action: "agent",
      message: "NO_REPLY",
      name: "Sentry",
      wakeMode: "now",
      deliver: false,
    };
  }

  // 2) resolved event: ack-only
  if (action === "resolved") {
    return {
      action: "agent",
      message: "NO_REPLY",
      name: "Sentry",
      wakeMode: "now",
      deliver: false,
    };
  }

  const deliveryInstructions = `\n\nDelivery (MANDATORY):\n1) 최종 요약문을 /tmp/sentry_summary.txt 에 저장\n2) 아래 명령으로 main profile을 통해 ${DELIVERY_CHANNEL} 채널로 전송\n   openclaw --profile main message send --channel ${DELIVERY_CHANNEL} --target ${DELIVERY_TARGET} --message "$(cat /tmp/sentry_summary.txt)"\n3) 전송 성공 시 최종 응답은 정확히 NO_REPLY\n4) 전송 실패 시 최종 응답은 한 줄만: \"🚨 sentry-delivery-failed: <에러요약>\"`;

  // 3) incomplete payload: tiny report + delegated delivery
  const isThin = !title && !culprit && !issueId;
  if (isThin) {
    return {
      action: "agent",
      message:
        `아래 문장을 그대로 최종 요약문으로 사용하라:\n실제 알림이지만 webhook payload가 불완전합니다. issue/latest event 원문 조회가 필요합니다.` +
        deliveryInstructions,
      name: "Sentry",
      wakeMode: "now",
      deliver: false,
    };
  }

  // 4) triage prompt (runbook-first)
  const runbookPath = process.env.SENTRY_RUNBOOK_PATH
    || "/Users/juucheol/.openclaw/workspace/SENTRY_RUNBOOK.md";

  const message = `/think medium\nSentry triage\n\nInput:\n- action=${action}\n- issueId=${issueId || "unknown"}\n- shortId=${shortId || "unknown"}\n- project=${project || "unknown"}\n- title=${title || "unknown"}\n- level=${level || "unknown"}\n- culprit=${culprit || "unknown"}\n- issueUrl=${issueUrl || "unknown"}\n\nStep 0 (MANDATORY):\n- ${runbookPath} 를 먼저 읽고 그대로 따른다.\n- 이 단계는 매 hook마다 반복한다(캐시/기억 의존 금지).\n\nRules:\n1) webhook-only 분류 금지: issue + latest event API 원문 조회 필수.\n2) 환경증거(host/release/tag/url/breadcrumb) 먼저 확정 후 분류.\n3) API 관련은 4개 repo 교차검증:\n   ~/Bootalk/frontend-monorepo\n   ~/Bootalk/btalk2.1_backend\n   ~/Bootalk/legacy-service\n   ~/Bootalk/bootalk-amplify\n4) 일시적(transient) 판단은 근거 부족 시 금지. 확신 없으면 actionable/open 유지.\n5) 정확판단에 DB 검증 필요 시 ~/.claude/credentials 를 사용해 pymysql 읽기전용 SELECT만 수행.\n   - 쓰기/삭제/DDL 금지\n6) DynamoDB/bootalk-amplify 관련은 AWS CLI 읽기 조회로 교차검증. 파괴적 명령 금지.\n7) 브랜치 정책: main 직접 타겟 금지. PR은 integration branch(기본 develop) 대상.\n8) 환경 게이트:\n   - production-like actionable: fix + PR + resolve(inNextRelease, 실패 시 now fallback)\n   - development-like: GitHub PR/Issue 생성 금지 (githubActivity=none)\n9) 기록 의무:\n   - memory/sentry/incidents-YYYY-MM.jsonl 1줄\n   - memory/pr-history.md 업데이트(필수)\n\nFinal reply format (developer-readable):\n- Issue: <issueId> (<shortId>, <project>)\n- Event: <eventId>\n- Environment proof: <prod/dev 근거 host/release/tag/url/breadcrumb>\n- Classification: <lineageKey> | <verdict>\n- Verification: <issue/latest-event + 4repo + (DB/AWS if used)>\n- Action: <fix+PR+resolve 또는 keep_open/resolve + githubActivity=none(dev-policy), fallback/기록 여부>\n\nConstraints:\n- 한국어\n- 6~12줄\n- 파이프(|) 한 줄 압축 포맷 금지` + deliveryInstructions;

  return {
    action: "agent",
    message,
    name: "Sentry",
    wakeMode: "now",
    deliver: false,
  };
}
