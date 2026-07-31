import katex from "katex";

export default function ProblemDisplay({ questionText }) {
  const html = katex.renderToString(questionText, { throwOnError: false });

  return (
    <div
      className="rounded-lg border border-gray-200 bg-white p-4 text-xl"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
