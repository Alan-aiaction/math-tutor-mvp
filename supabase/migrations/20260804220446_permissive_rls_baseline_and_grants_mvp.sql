-- TEMPORARY: MVP-permissive RLS baseline (#10). No real identity to scope to yet
-- (#50/#51 add a real access-code-scoped policy later). service_role already
-- bypasses RLS regardless of these policies (see #13's grant migration).

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO anon, authenticated;

CREATE POLICY "mvp_permissive_all" ON public.problems
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
COMMENT ON POLICY "mvp_permissive_all" ON public.problems IS 'TEMPORARY: MVP-permissive baseline, see #51';

CREATE POLICY "mvp_permissive_all" ON public.attempts
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
COMMENT ON POLICY "mvp_permissive_all" ON public.attempts IS 'TEMPORARY: MVP-permissive baseline, see #51';

CREATE POLICY "mvp_permissive_all" ON public.attempt_steps
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
COMMENT ON POLICY "mvp_permissive_all" ON public.attempt_steps IS 'TEMPORARY: MVP-permissive baseline, see #51';

CREATE POLICY "mvp_permissive_all" ON public.misconception_rules
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
COMMENT ON POLICY "mvp_permissive_all" ON public.misconception_rules IS 'TEMPORARY: MVP-permissive baseline, see #51';

CREATE POLICY "mvp_permissive_all" ON public.hints
  FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);
COMMENT ON POLICY "mvp_permissive_all" ON public.hints IS 'TEMPORARY: MVP-permissive baseline, see #51';
