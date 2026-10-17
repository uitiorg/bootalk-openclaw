export default function transform() {
  return {
    action: "agent",
    message: "NO_REPLY",
    name: "Sentry",
    wakeMode: "now",
    deliver: false,
  };
}
