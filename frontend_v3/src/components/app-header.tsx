import Link from 'next/link';
import { Logo } from '@/components/icons/logo';

export default function AppHeader({ children }: { children?: React.ReactNode }) {
  return (
    <header className="border-b print:hidden">
      <div className="container mx-auto px-4 py-4 flex items-center gap-4">
        <Logo className="h-8 w-8 text-primary" />
        <h1 className="font-headline text-2xl font-bold text-foreground">
          Autonomax
        </h1>
        <nav className="ml-auto flex items-center gap-4 text-sm">
          <Link href="/shop" className="text-muted-foreground hover:text-foreground">Shop</Link>
          <Link href="/commerce" className="text-muted-foreground hover:text-foreground">Commerce</Link>
          <Link href="/alexandria" className="text-muted-foreground hover:text-foreground">Alexandria</Link>
          <Link href="/opportunities" className="text-muted-foreground hover:text-foreground">Opportunities</Link>
          <Link href="/dashboard" className="text-muted-foreground hover:text-foreground">Dashboard</Link>
        </nav>
        {children}
      </div>
    </header>
  );
}
