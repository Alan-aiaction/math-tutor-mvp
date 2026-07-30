import StepBox from "./StepBox";

export default function StepList({ steps, onDelete }) {
  return (
    <div className="flex w-full max-w-md flex-col gap-3">
      {steps.map((step, index) => (
        <StepBox
          key={index}
          index={index}
          status={step.status}
          onDelete={onDelete ? () => onDelete(index) : undefined}
        />
      ))}
    </div>
  );
}
