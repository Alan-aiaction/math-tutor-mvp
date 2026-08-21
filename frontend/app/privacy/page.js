"use client";

import { useLanguage } from "../lib/LanguageContext";

// GDPR/AVG privacy statement (3rd MVP). A real Next.js route, not part of the
// single-page `/` app - reachable with no session at all, since a privacy statement
// has to be checkable before anyone creates an account, not just after.
//
// Content is two full JSX blocks switched on `lang`, not routed through translations.js's
// t() key system - that system is built for short UI labels with {param} interpolation,
// and forcing multi-paragraph legal-style prose into single-line string keys would make
// it unreviewable. A deliberate, scoped exception to the usual i18n convention.
//
// Every factual claim below is grounded in what's actually true in this codebase today
// (see decision-log.md's "GDPR/AVG - privacy statement" entry for what was verified and
// how) - two facts are still placeholders pending real input from Alan, marked clearly
// below rather than invented: the contact email and the Supabase hosting region.
export default function PrivacyPage() {
  const { lang } = useLanguage();

  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-8 text-left md:p-16">
      <div className="flex w-full max-w-2xl flex-col gap-6">
        <a href="/" className="self-start text-sm font-bold text-ink-muted hover:underline">
          {lang === "nl" ? "← Terug" : "← Back"}
        </a>
        {lang === "nl" ? <DutchContent /> : <EnglishContent />}
      </div>
    </main>
  );
}

function Section({ title, children }) {
  return (
    <section className="flex flex-col gap-2 rounded-2xl border border-border bg-bg p-6">
      <h2 className="font-display text-base font-bold text-ink">{title}</h2>
      <div className="flex flex-col gap-2 text-sm text-ink-muted">{children}</div>
    </section>
  );
}

function DutchContent() {
  return (
    <>
      <h1 className="font-display text-2xl font-bold text-ink">Privacybeleid</h1>

      <Section title="Wie zijn wij">
        <p>
          Math Tutor MVP is een klein, in ontwikkeling zijnd oefenprogramma voor
          rekenen (groep 7-8), gemaakt door Alan. Voor vragen over dit privacybeleid of
          over je gegevens: [privacy contactadres nog te bevestigen].
        </p>
      </Section>

      <Section title="Welke gegevens verzamelen we">
        <p>Van de ouder: het e-mailadres waarmee het account is aangemaakt.</p>
        <p>
          Van een kind: alleen een bijnaam (nooit een echte naam, e-mailadres of
          geboortedatum - die vragen we niet uit). Daarnaast: welke oefenstappen zijn
          gemaakt, of ze goed of fout waren, hoe vaak een stap opnieuw is geprobeerd, en
          wanneer.
        </p>
      </Section>

      <Section title="Wat we bewust niet verzamelen">
        <p>
          De ruwe pentekening die je kind maakt om een antwoord te herkennen (handschrift-
          herkenning) wordt nooit opgeslagen of gelogd - alleen het herkende antwoord zelf
          blijft bewaard, en dat alleen na bevestiging.
        </p>
      </Section>

      <Section title="Waarom we deze gegevens gebruiken">
        <p>
          Om het oefenprogramma te laten werken, en om een ouder inzicht te geven in de
          voortgang van hun kind.
        </p>
      </Section>

      <Section title="Hoe lang we gegevens bewaren">
        <p>
          Zolang het kind-account bestaat. Verwijdert een ouder een kind (via "Mijn
          kinderen"), dan worden dat kind en al hun oefengegevens direct en permanent
          verwijderd.
        </p>
      </Section>

      <Section title="Toestemming">
        <p>
          Alleen een ouder of wettelijk vertegenwoordiger kan een kind-account
          aanmaken - een kind kan dit nooit zelf. Het aanmaken van een kind-account is
          het toestemmingsmoment. Toestemming intrekken kan altijd, door het kind te
          verwijderen via "Mijn kinderen".
        </p>
      </Section>

      <Section title="Jouw rechten">
        <p>
          Inzage en verwijdering kun je zelf regelen in de app (Mijn kinderen, Account).
          Voor andere verzoeken (bijvoorbeeld correctie): [privacy contactadres nog te
          bevestigen].
        </p>
      </Section>

      <Section title="Waar gegevens worden opgeslagen">
        <p>
          We slaan geen onnodige of gevoelige gegevens op - alleen wat nodig is om de
          app te laten werken. Alles wordt veilig bewaard in [regio nog te bevestigen].
        </p>
      </Section>
    </>
  );
}

function EnglishContent() {
  return (
    <>
      <h1 className="font-display text-2xl font-bold text-ink">Privacy Policy</h1>

      <Section title="Who we are">
        <p>
          Math Tutor MVP is a small, in-development math practice tool for Dutch groep
          7-8 (roughly ages 10-12), built by Alan. For questions about this policy or
          your data: [privacy contact email - to be confirmed].
        </p>
      </Section>

      <Section title="What we collect">
        <p>From the parent: the email address used to create the account.</p>
        <p>
          From a child: only a nickname (never a real name, email, or birthdate - we
          never ask for those). Beyond that: which practice steps were attempted,
          whether they were correct, how many retries each step took, and when.
        </p>
      </Section>

      <Section title="What we deliberately don't collect">
        <p>
          The raw ink drawing your child makes for handwriting recognition is never
          stored or logged - only the recognized answer itself is kept, and only after
          confirmation.
        </p>
      </Section>

      <Section title="Why we use this data">
        <p>To run the practice tool itself, and to show a parent their child's progress.</p>
      </Section>

      <Section title="How long we keep data">
        <p>
          For as long as the child's account exists. If a parent removes a child (via
          "My children"), that child and all their practice data are deleted
          immediately and permanently.
        </p>
      </Section>

      <Section title="Consent">
        <p>
          Only a parent or legal guardian can create a child's account - a child can
          never do this themselves. Creating a child's account is the consent act.
          Consent can be withdrawn at any time by removing that child via "My
          children."
        </p>
      </Section>

      <Section title="Your rights">
        <p>
          Access and deletion are self-service, right in the app (My children,
          Account). For anything else (e.g. correction requests): [privacy contact
          email - to be confirmed].
        </p>
      </Section>

      <Section title="Where data is stored">
        <p>
          We don't store any unnecessary or sensitive data - only what's needed to run
          the app. Everything is stored securely in [region to be confirmed].
        </p>
      </Section>
    </>
  );
}
