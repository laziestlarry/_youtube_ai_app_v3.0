import { Logo } from '@/components/icons/logo';

export default function AppHeader({ children }: { children?: React.ReactNode }) {
  return (
    <header className="border-b print:hidden">
      <div className="container mx-auto px-4 py-4 flex items-center gap-4">
        <Logo className="h-8 w-8 text-primary" />
        <h1 className="font-headline text-2xl font-bold text-foreground">
          BizOp Navigator
        </h1>
        {children}
      </div>
    </header>
  );
}
