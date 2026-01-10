import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

// Get API key from environment
const apiKey = process.env.GEMINI_API_KEY;

// Validate API key
if (!apiKey) {
  console.error('❌ GEMINI_API_KEY is not set!');
  console.error('📝 Please add GEMINI_API_KEY to your .env.local file');
  console.error('🔗 Get your key at: https://aistudio.google.com/app/apikey');
} else if (apiKey.length < 30) {
  console.error('❌ GEMINI_API_KEY appears to be invalid (too short)');
  console.error('🔗 Get a new key at: https://aistudio.google.com/app/apikey');
} else {
  console.log('✅ GEMINI_API_KEY loaded successfully');
}

export const ai = genkit({
  plugins: [
    googleAI({
      apiKey: apiKey || 'PLACEHOLDER_KEY_NOT_SET',
    }),
  ],
});
