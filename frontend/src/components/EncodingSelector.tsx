import type { SupportedEncoding } from "../types/api";

interface EncodingSelectorProps {
  encodings: SupportedEncoding[];
  value: SupportedEncoding;
  onChange: (encoding: SupportedEncoding) => void;
}

function EncodingSelector({ encodings, value, onChange }: EncodingSelectorProps) {
  return (
    <label>
      Encoding
      <select
        aria-label="Encoding"
        value={value}
        onChange={(event) => onChange(event.target.value as SupportedEncoding)}
      >
        {encodings.map((encoding) => (
          <option key={encoding} value={encoding}>
            {encoding}
          </option>
        ))}
      </select>
    </label>
  );
}

export default EncodingSelector;
