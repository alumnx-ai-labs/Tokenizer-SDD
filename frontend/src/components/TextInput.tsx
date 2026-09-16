interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
}

function TextInput({ value, onChange }: TextInputProps) {
  return (
    <textarea
      aria-label="Text to tokenize"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      rows={10}
      style={{ width: "100%" }}
      className="text-input"
    />
  );
}

export default TextInput;
