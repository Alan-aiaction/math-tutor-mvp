"use client";

import { useEffect, useRef, useState } from "react";

// Deliberately a plain <canvas> + Pointer Events capture, not MyScript's own
// web SDK. The SDK talks to MyScript's cloud directly from the browser,
// which would mean exposing MYSCRIPT_APP_KEY/HMAC_KEY client-side - task #48
// (already Done) requires those stay server-side only. Capturing raw strokes
// here and sending them to our own POST /recognize (#19) keeps the keys on
// the backend, where recognize_math() (#18) already knows how to use them.
//
// `responsive` (ticket #74 follow-up) is opt-in and only used by ScratchPad.
// When false (the default - StepBox's exact existing usage), this renders
// the same fixed-size <canvas> as before, byte-for-byte. When true, the
// canvas's width/height attributes (its drawing-buffer resolution) track a
// wrapper element's real measured size via ResizeObserver instead of fixed
// props. Changing those attributes clears the browser's own canvas content
// (standard behavior), so every resize redraws from strokesRef - the raw
// stroke point-data survives independently of the pixels.
export default function InkCanvas({ width = 400, height = 160, responsive = false, onStrokesChange }) {
  const canvasRef = useRef(null);
  const canvasWrapRef = useRef(null);
  const strokesRef = useRef([]);
  const currentStrokeRef = useRef(null);
  const [isEmpty, setIsEmpty] = useState(true);
  const [measuredSize, setMeasuredSize] = useState({ width, height });

  const canvasWidth = responsive ? measuredSize.width : width;
  const canvasHeight = responsive ? measuredSize.height : height;

  const getContext = () => canvasRef.current.getContext("2d");

  const drawStroke = (ctx, stroke) => {
    if (stroke.x.length === 0) return;
    ctx.beginPath();
    ctx.moveTo(stroke.x[0], stroke.y[0]);
    for (let i = 1; i < stroke.x.length; i++) {
      ctx.lineTo(stroke.x[i], stroke.y[i]);
    }
    ctx.strokeStyle = "#1c2b27";
    ctx.lineWidth = 2;
    ctx.lineCap = "round";
    ctx.stroke();
  };

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
    getContext().clearRect(0, 0, canvasWidth, canvasHeight);
    onStrokesChange?.([]);
  };

  useEffect(() => {
    if (!responsive) return;
    const wrap = canvasWrapRef.current;
    if (!wrap) return;
    const observer = new ResizeObserver((entries) => {
      const { width: w, height: h } = entries[0].contentRect;
      setMeasuredSize((prev) => {
        const next = { width: Math.round(w), height: Math.round(h) };
        if (prev.width === next.width && prev.height === next.height) return prev;
        return next;
      });
    });
    observer.observe(wrap);
    return () => observer.disconnect();
  }, [responsive]);

  // Runs after every measured-size change, i.e. right after the browser has
  // cleared the canvas in response to the width/height attribute change above.
  useEffect(() => {
    if (!responsive) return;
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;
    for (const stroke of strokesRef.current) {
      drawStroke(ctx, stroke);
    }
  }, [responsive, canvasWidth, canvasHeight]);

  if (responsive) {
    return (
      <div className="flex h-full w-full flex-col gap-2">
        <div ref={canvasWrapRef} className="min-h-0 flex-1">
          <canvas
            ref={canvasRef}
            width={canvasWidth}
            height={canvasHeight}
            onPointerDown={startStroke}
            onPointerMove={extendStroke}
            onPointerUp={endStroke}
            onPointerLeave={endStroke}
            className="h-full w-full touch-none rounded-md border border-gray-300 bg-white"
            aria-label="Draw your answer here"
          />
        </div>
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

  return (
    <div className="flex flex-col gap-2">
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
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
