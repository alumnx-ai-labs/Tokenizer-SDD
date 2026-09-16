interface ResetVocabularyButtonProps {
  onConfirm: () => void;
}

function ResetVocabularyButton({ onConfirm }: ResetVocabularyButtonProps) {
  function handleClick() {
    if (window.confirm("Reset the custom vocabulary to its initial state? This cannot be undone.")) {
      onConfirm();
    }
  }

  return (
    <button type="button" className="reset-vocabulary-button" onClick={handleClick}>
      Reset Vocabulary
    </button>
  );
}

export default ResetVocabularyButton;
