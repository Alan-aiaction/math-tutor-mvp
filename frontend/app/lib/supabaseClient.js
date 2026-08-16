import { createClient } from "@supabase/supabase-js";

// 3rd MVP: the frontend talks to Supabase Auth directly (anon key - safe to expose
// client-side, that's what it's for) for parent sign-up/sign-in only. Everything else
// (children, attempts) goes through the FastAPI backend, which verifies the resulting
// access token itself (backend/auth.py) rather than trusting the frontend.
//
// Supabase's client persists the session in localStorage by default - this is what makes
// "parent stays logged in" work with zero custom code.
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);
