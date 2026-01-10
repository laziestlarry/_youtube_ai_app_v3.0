const DEFAULT_BACKEND_URL = '';

type FetchJsonOptions = RequestInit & {
  timeoutMs?: number;
};

export function getBackendUrl(): string {
  return (
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    DEFAULT_BACKEND_URL
  );
}

export function buildBackendUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path;
  }
  if (path.startsWith('/')) {
    return `${getBackendUrl()}${path}`;
  }
  return `${getBackendUrl()}/${path}`;
}

async function fetchJson<T>(path: string, options: FetchJsonOptions = {}): Promise<T> {
  const { timeoutMs = 15000, headers, ...init } = options;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(buildBackendUrl(path), {
      ...init,
      headers: {
        ...headers,
      },
      signal: controller.signal,
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`Backend request failed (${response.status}): ${errorBody || response.statusText}`);
    }

    return (await response.json()) as T;
  } finally {
    clearTimeout(timeout);
  }
}

export async function postJson<T>(path: string, body: unknown, options: FetchJsonOptions = {}): Promise<T> {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  return fetchJson<T>(path, {
    ...options,
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
}

export async function getJson<T>(path: string, options: FetchJsonOptions = {}): Promise<T> {
  return fetchJson<T>(path, {
    ...options,
    method: 'GET',
  });
}

export type { FetchJsonOptions };
