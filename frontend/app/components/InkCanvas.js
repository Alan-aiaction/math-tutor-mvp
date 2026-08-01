"use client";

import { useRef, useState } from "react";

// Deliberately a plain <canvas> + Pointer Events capture, not MyScript's own
// web SDK. The SDK talks to MyScript's cloud directly from the browser,
// which would mean exposing MYSCRIPT_APP_KEY/HMAC_KEY client-side - task #48
// (already Done) requires those stay server-side only. Capturing raw strokes
// here and sending them to our own POST /recognize (#19) keeps the keys on
// the backend, where recognize_math() (#18) already knows how to use them.
export default function InkCanvas({ width = 400, height = 160, onStrokesChange }) {
  const canvasRef = useRef(null);
  const strokesRef = useRef([]);
  const currentStrokeRef = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);

  const getContext = () => canvasRef.current.getContext("2d");

  const startStroke = (e) => {
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    currentStrokeRef.current = {
      x: [x],
      y: [y],
      t: [performance.now()],
      pointerType: e.pointerType,
    };
    const ctx = getContext();
    ctx.beginPath();
    ctx.moveTo(x, y);
    canvasRef.current.setPointerCapture(e.pointerId);
  };

  const extendStroke = (e) => {
    if (!currentStrokeRef.current) return;
    const rect = canvasRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    currentStrokeRef.current.x.push(x);
    currentStrokeRef.current.y.push(y);
    currentStrokeRef.current.t.push(performance.now());

    const ctx = getContext();
    ctx.lineTo(x, y);
    ctx.strokeStyle = "#1c2b27";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.stroke();
  };

  const endStroke = () => {
    if (!currentStrokeRef.current) return;
    strokesRef.current.push(currentStrokeRef.current);
    currentStrokeRef.current = null;
    setIsEmpty(false);
    onStrokesChange?.(getStrokeGroups());
  };

  const getStrokeGroups = () => {
    if (strokesRef.current.length === 0) return [];
    return [{ penStyle: null, strokes: strokesRef.current }];
  };

  const clear = () => {
    strokesRef.current = [];
    currentStrokeRef.current = null;
    setIsEmpty(true);
    getContext().clearRect(0, 0, width, height);
    onStrokesChange?.([]);
  };

  return (
    <div className="flex flex-col gap-2">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onPointerDown={startStroke}
        onPointerMove={extendStroke}
        onPointerUp={endStroke}
        onPointerLeave={endStroke}
        className="touch-none rounded-md border border-gray-300 bg-white"
        aria-label="Draw your answer here"
      />
      <button
        type="button"
        onClick={clear}
        disabled={isEmpty}
        className="self-start text-xs font-medium text-gray-500 hover:text-red-500 disabled:opacity-40 disabled:hover:text-gray-500"
      >
        Clear drawing
      </button>
    </div>
  );
}
