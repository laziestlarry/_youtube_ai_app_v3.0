import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';

const PricingPage: React.FC = () => {
    const [selectedPlan, setSelectedPlan] = useState<string>('');
    const [loading, setLoading] = useState(false);

    const pricingTiers = [
        {
            id: 'starter',
            name: 'Starter',
            price: 29,
            features: [
                '5 videos per month',
                'Basic AI models',
                'Email support',
                'Basic analytics'
            ]
        },
        {
            id: 'professional',
            name: 'Professional',
            price: 99,
            features: [
                '20 videos per month',
                'Advanced AI models',
                'Priority support',
                'Advanced analytics',
                'Revenue optimization',
                '10% revenue share on earnings > $1000'
            ],
            popular: true
        },
        {
            id: 'enterprise',
            name: 'Enterprise',
            price: 299,
            features: [
                'Unlimited videos',
                'All AI models',
                'Dedicated support',
                'Enterprise analytics',
                '5% revenue share on earnings > $1000',
                'White-label options',
                'API access'
            ]
        }
    ];

    const handleSubscribe = async (planId: string) => {
        setLoading(true);
        try {
            // TODO: Get user ID/Email from auth context
            const response = await fetch('http://localhost:8000/api/subscriptions/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plan_id: planId })
            });

            const { client_secret, customer_id, subscription_id } = await response.json();

            const stripe = await loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || '');
            if (stripe) {
                const { error } = await stripe.confirmCardPayment(client_secret);
                if (error) {
                    console.error('Payment failed:', error);
                } else {
                    // Redirect to dashboard
                    window.location.href = '/dashboard';
                }
            }

        } catch (error) {
            console.error('Subscription error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center">
                <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
                    Choose Your Plan
                </h2>
                <p className="mt-4 text-xl text-gray-600">
                    Start creating AI-powered YouTube content today
                </p>
            </div>

            <div className="mt-12 grid gap-8 lg:grid-cols-3">
                {pricingTiers.map((plan) => (
                    <div
                        key={plan.id}
                        className={`relative bg-white rounded-lg shadow-lg p-8 ${plan.popular ? 'ring-2 ring-blue-500' : ''
                            }`}
                        style={{ border: '1px solid #e5e7eb' }} // Simple fallback style
                    >
                        {plan.popular && (
                            <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                                <span className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                                    Most Popular
                                </span>
                            </div>
                        )}

                        <div className="text-center">
                            <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                            <div className="mt-4">
                                <span className="text-4xl font-extrabold text-gray-900">${plan.price}</span>
                                <span className="text-gray-500">/month</span>
                            </div>
                        </div>

                        <ul className="mt-8 space-y-4">
                            {plan.features.map((feature) => (
                                <li key={feature} className="flex items-center">
                                    <span className="text-green-500 mr-2">✓</span>
                                    <span className="ml-3 text-gray-700">{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <button
                            onClick={() => handleSubscribe(plan.id)}
                            disabled={loading}
                            className={`mt-8 w-full py-3 px-4 rounded-md font-medium ${plan.popular
                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                : 'bg-gray-800 text-white hover:bg-gray-900'
                                } disabled:opacity-50`}
                        >
                            {loading ? 'Processing...' : 'Get Started'}
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default PricingPage;
