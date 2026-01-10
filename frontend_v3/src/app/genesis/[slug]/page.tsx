import Link from "next/link";
import AppHeader from "@/components/app-header";
import { Button } from "@/components/ui/button";

const DEFAULT_BACKEND_URL = "http://localhost:8000";

function getBackendUrl(): string {
  return (
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.BACKEND_URL ||
    DEFAULT_BACKEND_URL
  );
}

function titleFromSlug(slug: string): string {
  return slug
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

type GenesisPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return [
    { slug: 'setup' },
    { slug: 'launch' },
    { slug: 'complete' },
    { slug: 'error' },
    { slug: 'default' },
  ];
}

export default async function GenesisPage({ params }: GenesisPageProps) {
  const { slug } = await params;
  const safeSlug = slug || "genesis";
  const title = titleFromSlug(safeSlug);
  const storefrontUrl = `${getBackendUrl()}/`;

  return (
    <div className="min-h-screen bg-background text-foreground">
      <AppHeader />
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl">
          <p className="text-sm uppercase tracking-[0.35em] text-muted-foreground">
            Genesis Protocol
          </p>
          <h1 className="mt-4 text-4xl font-headline font-bold">
            Genesis Live: {title}
          </h1>
          <p className="mt-4 text-muted-foreground">
            The Genesis build finished successfully. Your operational hub is
            active and linked to live commerce routes.
          </p>

          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button asChild>
              <a href={storefrontUrl} target="_blank" rel="noopener">
                Open Storefront
              </a>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/dashboard">Return to Dashboard</Link>
            </Button>
          </div>

          <div className="mt-10 rounded-xl border border-border bg-muted/30 p-6">
            <h2 className="text-lg font-semibold">Next Actions</h2>
            <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
              <li>Verify checkout flow on Shopier for the top offer.</li>
              <li>Publish the Etsy listings from the CSV export.</li>
              <li>Run the weekly Chimera ops cycle for updates.</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
