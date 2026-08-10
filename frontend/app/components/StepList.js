import StepBox from "./StepBox";

export default function StepList({ steps, results, onDelete, onStepChange, problemId }) {
  return (
    <div className="flex w-full max-w-md flex-col gap-3">
      {steps.map((step, index) => (
        <StepBox
          // Remounting on problemId change (not just index) clears StepBox's own local
          // state (recognised value, draft, drawing/editing mode, ink strokes) whenever a
          // new problem loads - that state lives inside StepBox, not in this array, so
          // resetting `steps` alone doesn't touch it.
          key={`${problemId}-${index}`}
          index={index}
          status={step.status}
          recognizedLatex={step.recognizedLatex}
          result={results ? results[index] : null}
          onDelete={onDelete ? () => onDelete(index) : undefined}
          onChange={onStepChange ? (value) => onStepChange(index, value) : undefined}
        />
      ))}
    </div>
  );
}
