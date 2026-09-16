interface ErrorMessageProps {
  errorCode: string;
  detail: string;
}

function ErrorMessage({ errorCode, detail }: ErrorMessageProps) {
  return (
    <div role="alert" className="error-message">
      <strong>{errorCode}</strong>: {detail}
    </div>
  );
}

export default ErrorMessage;
