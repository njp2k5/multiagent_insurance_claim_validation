/**
 * Sends a log message to the Vite dev server terminal via POST /__log.
 * Falls back silently in production or if the dev server is unreachable.
 *
 * Usage:  terminalLog("ClaimStart", "Initialized with claimId:", claimId);
 */
export function terminalLog(tag: string, ...args: unknown[]): void {
  // Also keep it in the browser console for convenience
  console.log(`[${tag}]`, ...args);

  // Fire-and-forget POST to the Vite dev server
  try {
    const payload = JSON.stringify({
      tag,
      args: args.map((a) =>
        typeof a === "object" ? JSON.stringify(a) : String(a ?? "")
      ),
    });
    fetch("/__log", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload,
    }).catch(() => {
      /* dev server unreachable – ignore */
    });
  } catch {
    /* ignore in production builds */
  }
}
