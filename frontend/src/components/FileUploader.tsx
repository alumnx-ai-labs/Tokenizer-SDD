interface FileUploaderProps {
  accept: string;
  onChange: (file: File | null) => void;
}

function FileUploader({ accept, onChange }: FileUploaderProps) {
  return (
    <input
      type="file"
      aria-label="Upload file"
      accept={accept}
      onChange={(event) => onChange(event.target.files?.[0] ?? null)}
    />
  );
}

export default FileUploader;
