export default function ProblemDisplay({ questionText }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 text-xl">
      {questionText}
    </div>
  );
}
