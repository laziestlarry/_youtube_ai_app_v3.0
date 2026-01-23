'use client';

import { useState } from 'react';
import Link from 'next/link';
import AppHeader from '@/components/app-header';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const FEATURED_PRODUCTS = [
  {
    sku: 'ZEN-ART-BASE',
    title: 'Zen Art Printables Bundle',
    shortDesc: 'Minimalist wall art for calm, modern spaces',
    price: { regular: 79, sale: 29 },
    features: ['Instant Download', '5+ Sizes Included', 'Print Ready (300 DPI)'],
    cta: 'Download Now',
    urgency: '70% OFF Today Only',
    category: 'digital',
  },
  {
    sku: 'HYBRID-STACK-01',
    title: 'Hybrid Passive Income Stack',
    shortDesc: 'Complete playbook for automated side income',
    price: { regular: 199, sale: 49 },
    features: ['Step-by-Step Playbook', 'Automation Templates', 'Launch Checklists'],
    cta: 'Start Building Today',
    urgency: 'Limited Time Offer',
    category: 'digital',
  },
  {
    sku: 'CREATOR-KIT-01',
    title: 'Creator Starter Kit',
    shortDesc: 'Launch your first digital product this week',
    price: { regular: 149, sale: 49 },
    features: ['Launch Templates', 'Content Calendar', 'Pricing Strategies'],
    cta: 'Get the Kit',
    urgency: 'Best Seller',
    category: 'digital',
  },
  {
    sku: 'NOTION-PASSIVE-01',
    title: 'Notion Passive Income Dashboard',
    shortDesc: 'Track all your income streams in one place',
    price: { regular: 99, sale: 29 },
    features: ['Revenue Tracking', 'Content Planner', 'KPI Dashboard'],
    cta: 'Get Organized',
    urgency: 'New Release',
    category: 'digital',
  },
];

const SERVICE_PRODUCTS = [
  {
    sku: 'YT-AUTO-01',
    title: 'YouTube Automation Studio',
    shortDesc: 'End-to-end YouTube content automation',
    price: { min: 299, max: 1499 },
    features: ['Content Strategy', 'Script Writing', 'Thumbnail Design', 'Publishing Workflow'],
    cta: 'Scale Your Channel',
    category: 'service',
  },
  {
    sku: 'IW-CONSULT-01',
    title: 'IntelliWealth AI Consulting',
    shortDesc: '90-day AI transformation for executive teams',
    price: { min: 15000, max: 50000 },
    features: ['Discovery & Blueprint', 'Implementation Sprint', 'KPI Dashboards', 'Ongoing Advisory'],
    cta: 'Book Discovery Call',
    category: 'consulting',
  },
];

const VALUE_PROPS = [
  { icon: '⚡', title: 'Instant Delivery', desc: 'Download immediately after purchase' },
  { icon: '🛡️', title: '30-Day Guarantee', desc: 'Full refund if not satisfied' },
  { icon: '💬', title: '24h Support', desc: 'Questions answered within a day' },
];

const TESTIMONIALS = [
  {
    quote: 'Launched my first product in 5 days instead of 5 weeks. The templates are gold.',
    author: 'Mike T.',
    role: 'Creator',
    rating: 5,
  },
  {
    quote: 'Finally, wall art that actually brings calm to my workspace. Beautiful quality.',
    author: 'Sarah K.',
    role: 'Remote Worker',
    rating: 5,
  },
  {
    quote: 'The automation playbook paid for itself in the first week. Highly recommend.',
    author: 'Jessica R.',
    role: 'Entrepreneur',
    rating: 5,
  },
];

export default function DropPage() {
  const [email, setEmail] = useState('');

  const handleCheckout = (sku: string) => {
    // In production, this would redirect to Shopier or payment processor
    window.location.href = `/shop?checkout=${sku}`;
  };

  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-background to-muted/30">
      <AppHeader />

      <main className="flex-1">
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-12 md:py-20">
          <div className="mx-auto max-w-4xl text-center">
            <Badge variant="secondary" className="mb-4 px-4 py-1">
              🔥 Flash Sale: Up to 70% Off Everything
            </Badge>
            <h1 className="font-headline text-4xl font-bold tracking-tight md:text-6xl">
              Transform Your Space.
              <br />
              <span className="text-primary">Automate Your Income.</span>
            </h1>
            <p className="mt-4 text-lg text-muted-foreground md:text-xl">
              Premium digital products, creator kits, and automation systems.
              <br />
              Instant download. Real results.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" className="px-8" onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}>
                Shop Best Sellers
              </Button>
              <Button size="lg" variant="outline" className="px-8" onClick={() => document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' })}>
                View Services
              </Button>
            </div>
          </div>
        </section>

        {/* Social Proof Bar */}
        <section className="border-y bg-muted/50 py-4">
          <div className="container mx-auto px-4">
            <div className="flex flex-wrap items-center justify-center gap-8 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <span className="text-lg">⭐</span>
                <span>4.9/5 Average Rating</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg">👥</span>
                <span>2,500+ Happy Customers</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg">🌍</span>
                <span>47 Countries</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg">⚡</span>
                <span>Instant Digital Delivery</span>
              </div>
            </div>
          </div>
        </section>

        {/* Value Props */}
        <section className="container mx-auto px-4 py-12">
          <div className="grid gap-6 md:grid-cols-3">
            {VALUE_PROPS.map((prop) => (
              <Card key={prop.title} className="text-center">
                <CardContent className="pt-6">
                  <div className="text-4xl">{prop.icon}</div>
                  <h3 className="mt-4 font-semibold">{prop.title}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{prop.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Featured Products */}
        <section id="products" className="container mx-auto px-4 py-12">
          <div className="mb-8 text-center">
            <h2 className="font-headline text-3xl font-bold">Best Sellers</h2>
            <p className="mt-2 text-muted-foreground">
              Our most popular digital products - instant download, immediate value
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {FEATURED_PRODUCTS.map((product) => (
              <Card key={product.sku} className="relative flex flex-col overflow-hidden">
                {product.urgency && (
                  <Badge className="absolute right-2 top-2 z-10 bg-red-500 text-white">
                    {product.urgency}
                  </Badge>
                )}
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">{product.title}</CardTitle>
                  <CardDescription>{product.shortDesc}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col justify-between">
                  <ul className="mb-4 space-y-1 text-sm">
                    {product.features.map((f) => (
                      <li key={f} className="flex items-center gap-2">
                        <span className="text-green-500">✓</span> {f}
                      </li>
                    ))}
                  </ul>
                  <div>
                    <div className="mb-3 flex items-baseline gap-2">
                      <span className="text-2xl font-bold">${product.price.sale}</span>
                      <span className="text-sm text-muted-foreground line-through">
                        ${product.price.regular}
                      </span>
                    </div>
                    <Button className="w-full" onClick={() => handleCheckout(product.sku)}>
                      {product.cta}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Testimonials */}
        <section className="bg-muted/30 py-12">
          <div className="container mx-auto px-4">
            <div className="mb-8 text-center">
              <h2 className="font-headline text-3xl font-bold">What Customers Say</h2>
            </div>
            <div className="grid gap-6 md:grid-cols-3">
              {TESTIMONIALS.map((t, i) => (
                <Card key={i}>
                  <CardContent className="pt-6">
                    <div className="mb-2 text-yellow-500">{'★'.repeat(t.rating)}</div>
                    <p className="italic text-muted-foreground">"{t.quote}"</p>
                    <div className="mt-4">
                      <p className="font-semibold">{t.author}</p>
                      <p className="text-sm text-muted-foreground">{t.role}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Services Section */}
        <section id="services" className="container mx-auto px-4 py-12">
          <div className="mb-8 text-center">
            <h2 className="font-headline text-3xl font-bold">Premium Services</h2>
            <p className="mt-2 text-muted-foreground">
              Done-for-you solutions and expert consulting
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {SERVICE_PRODUCTS.map((product) => (
              <Card key={product.sku} className="flex flex-col">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>{product.title}</CardTitle>
                    <Badge variant="outline">{product.category}</Badge>
                  </div>
                  <CardDescription>{product.shortDesc}</CardDescription>
                </CardHeader>
                <CardContent className="flex flex-1 flex-col justify-between">
                  <ul className="mb-4 space-y-2">
                    {product.features.map((f) => (
                      <li key={f} className="flex items-center gap-2 text-sm">
                        <span className="text-green-500">✓</span> {f}
                      </li>
                    ))}
                  </ul>
                  <div>
                    <div className="mb-3">
                      <span className="text-sm text-muted-foreground">Starting at</span>
                      <p className="text-2xl font-bold">
                        ${product.price.min.toLocaleString()}
                        {product.price.max && (
                          <span className="text-base font-normal text-muted-foreground">
                            {' '}
                            - ${product.price.max.toLocaleString()}
                          </span>
                        )}
                      </p>
                    </div>
                    <Button className="w-full" variant="outline" onClick={() => handleCheckout(product.sku)}>
                      {product.cta}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Email Capture */}
        <section className="bg-primary py-12 text-primary-foreground">
          <div className="container mx-auto px-4 text-center">
            <h2 className="font-headline text-3xl font-bold">Get 20% Off Your First Order</h2>
            <p className="mt-2 opacity-90">
              Plus exclusive tips on automation and passive income
            </p>
            <form
              className="mx-auto mt-6 flex max-w-md flex-col gap-3 sm:flex-row"
              onSubmit={(e) => {
                e.preventDefault();
                // Handle email signup
                alert('Thanks! Check your email for your discount code.');
              }}
            >
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="flex-1 rounded-md px-4 py-2 text-foreground"
                required
              />
              <Button type="submit" variant="secondary" className="px-6">
                Get My 20% Off
              </Button>
            </form>
            <p className="mt-3 text-xs opacity-70">
              No spam. Unsubscribe anytime.
            </p>
          </div>
        </section>

        {/* FAQ */}
        <section className="container mx-auto px-4 py-12">
          <div className="mx-auto max-w-3xl">
            <h2 className="mb-8 text-center font-headline text-3xl font-bold">
              Frequently Asked Questions
            </h2>
            <div className="space-y-4">
              {[
                {
                  q: 'What do I receive after purchase?',
                  a: 'Digital products are delivered instantly via email and download page. Services include onboarding within 24-48 hours.',
                },
                {
                  q: 'Can I get a refund?',
                  a: 'Yes! All digital products have a 30-day money-back guarantee. If it doesn't work for you, we'll refund you.',
                },
                {
                  q: 'Do I need technical skills?',
                  a: 'Not at all. Our products come with step-by-step instructions and video walkthroughs.',
                },
                {
                  q: 'How do I contact support?',
                  a: 'Email us anytime. We respond within 24 hours on business days.',
                },
              ].map((faq, i) => (
                <Card key={i}>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base font-semibold">{faq.q}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{faq.a}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="container mx-auto px-4 py-12 text-center">
          <h2 className="font-headline text-3xl font-bold">Ready to Get Started?</h2>
          <p className="mt-2 text-muted-foreground">
            Join 2,500+ customers who've transformed their spaces and income
          </p>
          <Button size="lg" className="mt-6 px-8" onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}>
            Shop Now - Up to 70% Off
          </Button>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t bg-muted/30 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} AutonomaX Commerce. All rights reserved.</p>
          <p className="mt-2">
            Premium digital products, automation services, and AI consulting.
          </p>
          <div className="mt-4 flex justify-center gap-4">
            <Link href="/shop" className="hover:underline">
              Shop
            </Link>
            <Link href="/shop/drop" className="hover:underline">
              Deals
            </Link>
            <a href="mailto:support@autonomax.com" className="hover:underline">
              Support
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
