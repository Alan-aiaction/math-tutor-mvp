const STATUS_STYLES = {
  unanswered: {
    border: "border-gray-300",
    badge: "bg-gray-100 text-gray-500",
    icon: null,
    label: "Unanswered",
  },
  correct: {
    border: "border-green-400",
    badge: "bg-green-100 text-green-700",
    icon: "✓",
    label: "Correct",
  },
  incorrect: {
    border: "border-amber-400",
    badge: "bg-amber-100 text-amber-700",
    icon: "⚠",
    label: "Incorrect",
  },
};

export default function StepBox({ index, status = "unanswered" }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.unanswered;

  return (
    <div className={`rounded-lg border-2 p-4 ${style.border}`}>
      <div className="flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-gray-700">Step {index + 1}</span>
        <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${style.badge}`}>
          {style.icon && <span aria-hidden="true">{style.icon}</span>}
          {style.label}
        </span>
      </div>
    </div>
  );
}
