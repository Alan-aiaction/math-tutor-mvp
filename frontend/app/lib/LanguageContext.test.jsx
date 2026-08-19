import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { LanguageProvider, useLanguage } from "./LanguageContext";

const STORAGE_KEY = "mathTutorLanguage";

function Probe() {
  const { lang, setLang, t } = useLanguage();
  return (
    <div>
      <span data-testid="lang">{lang}</span>
      <span data-testid="translated">{t("nav.oefenen")}</span>
      <span data-testid="missing">{t("does.not.exist")}</span>
      <button onClick={() => setLang("en")}>Switch to English</button>
    </div>
  );
}

function renderProbe() {
  return render(
    <LanguageProvider>
      <Probe />
    </LanguageProvider>
  );
}

describe("LanguageContext", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("defaults to Dutch when nothing is persisted", () => {
    renderProbe();
    expect(screen.getByTestId("lang")).toHaveTextContent("nl");
    expect(screen.getByTestId("translated")).toHaveTextContent("Oefenen");
  });

  it("setLang switches the active language and every t() call updates with it", () => {
    renderProbe();
    fireEvent.click(screen.getByText("Switch to English"));
    expect(screen.getByTestId("lang")).toHaveTextContent("en");
    expect(screen.getByTestId("translated")).toHaveTextContent("Practice");
  });

  it("setLang persists the choice to localStorage", () => {
    renderProbe();
    fireEvent.click(screen.getByText("Switch to English"));
    expect(window.localStorage.getItem(STORAGE_KEY)).toBe("en");
  });

  it("reads a previously persisted language on mount", () => {
    window.localStorage.setItem(STORAGE_KEY, "en");
    renderProbe();
    expect(screen.getByTestId("lang")).toHaveTextContent("en");
    expect(screen.getByTestId("translated")).toHaveTextContent("Practice");
  });

  it("an unknown key falls back to the key itself, not a crash", () => {
    renderProbe();
    expect(screen.getByTestId("missing")).toHaveTextContent("does.not.exist");
  });
});
