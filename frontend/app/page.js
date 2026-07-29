import StepList from "./components/StepList";

const MOCK_STEPS = [
  { status: "correct" },
  { status: "incorrect" },
  { status: "unanswered" },
];

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center gap-8 p-16 text-center font-sans">
      <div>
        <h1 className="text-3xl font-semibold">Math Tutor MVP</h1>
        <p className="text-gray-600">Placeholder deployment — real UI coming in Phase 9.</p>
      </div>
      <StepList steps={MOCK_STEPS} />
    </main>
  );
}
