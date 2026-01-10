export function slugifyGenesis(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");
}

export function getGenesisBaseUrl(): string {
  if (typeof window !== "undefined") {
    return window.location.origin;
  }
  return (
    process.env.NEXT_PUBLIC_GENESIS_BASE_URL ||
    process.env.NEXT_PUBLIC_FRONTEND_URL ||
    ""
  );
}

export function buildGenesisUrl(name: string): string {
  const slug = slugifyGenesis(name || "genesis");
  const base = getGenesisBaseUrl();
  if (!base) {
    return `/genesis/${slug}`;
  }
  return `${base}/genesis/${slug}`;
}
