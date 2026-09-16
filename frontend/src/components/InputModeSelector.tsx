export type InputMode = "text" | "txt" | "pdf";

interface InputModeSelectorProps {
  mode: InputMode;
  onChange: (mode: InputMode) => void;
}

const OPTIONS: { value: InputMode; label: string }[] = [
  { value: "text", label: "Text" },
  { value: "txt", label: "TXT" },
  { value: "pdf", label: "PDF" },
];

function InputModeSelector({ mode, onChange }: InputModeSelectorProps) {
  return (
    <div role="tablist" aria-label="Input mode">
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          role="tab"
          aria-selected={mode === option.value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

export default InputModeSelector;
