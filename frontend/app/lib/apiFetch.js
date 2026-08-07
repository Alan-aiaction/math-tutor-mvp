const DEFAULT_TIMEOUT_MS = 15000;

export class ApiError extends Error {
  constructor(message, { isTimeout = false, status = null } = {}) {
    super(message);
    this.isTimeout = isTimeout;
    this.status = status;
  }
}

export async function apiFetch(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    if (!res.ok) {
      if (res.status >= 500) {
        throw new ApiError("Something went wrong on our end. Please try again in a moment.", {
          status: res.status,
        });
      }
      const body = await res.json().catch(() => ({}));
      throw new ApiError(body.detail || `Request failed (${res.status})`, { status: res.status });
    }
    return await res.json();
  } catch (err) {
    if (err.name === "AbortError") {
      throw new ApiError("This is taking longer than expected. Please try again.", { isTimeout: true });
    }
    if (err instanceof ApiError) throw err;
    throw new ApiError("Network error. Please check your connection and try again.");
  } finally {
    clearTimeout(timer);
  }
}
