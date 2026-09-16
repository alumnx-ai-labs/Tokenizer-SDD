import { useEffect, useState } from "react";
import Header from "./components/Header";
import TokenizerModeSelector, { type TokenizerMode } from "./components/TokenizerModeSelector";
import InputModeSelector, { type InputMode } from "./components/InputModeSelector";
import TextInput from "./components/TextInput";
import FileUploader from "./components/FileUploader";
import EncodingSelector from "./components/EncodingSelector";
import TokenizeButton from "./components/TokenizeButton";
import StatisticsPanel from "./components/StatisticsPanel";
import TokenVisualization from "./components/TokenVisualization";
import ErrorMessage from "./components/ErrorMessage";
import LoadingState from "./components/LoadingState";
import VocabularyPanel from "./components/VocabularyPanel";
import { useSessionId } from "./hooks/useSessionId";
import {
  ApiError,
  customTokenizeFile,
  customTokenizeText,
  getEncodings,
  tokenizeFile,
  tokenizeText,
} from "./api/client";
import type { CustomTokenizationResult, SupportedEncoding, TokenizationResult } from "./types/api";

function App() {
  const sessionId = useSessionId();
  const [tokenizerMode, setTokenizerMode] = useState<TokenizerMode>("tiktokenizer");
  const [inputMode, setInputMode] = useState<InputMode>("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [encodings, setEncodings] = useState<SupportedEncoding[]>([]);
  const [encoding, setEncoding] = useState<SupportedEncoding>("cl100k_base");
  const [result, setResult] = useState<TokenizationResult | CustomTokenizationResult | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [vocabularyRefreshKey, setVocabularyRefreshKey] = useState(0);

  useEffect(() => {
    getEncodings()
      .then((fetched) => {
        setEncodings(fetched);
        if (fetched.length > 0) {
          setEncoding(fetched[0]);
        }
      })
      .catch((err) => {
        if (err instanceof ApiError) {
          setError(err);
        }
      });
  }, []);

  function handleModeChange(mode: TokenizerMode) {
    setTokenizerMode(mode);
    setResult(null);
    setError(null);
  }

  async function handleTokenize() {
    setLoading(true);
    setError(null);
    try {
      let response: TokenizationResult | CustomTokenizationResult;
      if (tokenizerMode === "tiktokenizer") {
        if (inputMode === "text") {
          response = await tokenizeText(text, encoding);
        } else if (file) {
          response = await tokenizeFile(file, encoding);
        } else {
          return;
        }
      } else {
        if (inputMode === "text") {
          response = await customTokenizeText(text, sessionId);
        } else if (file) {
          response = await customTokenizeFile(file, sessionId);
        } else {
          return;
        }
      }
      setResult(response);
      if (tokenizerMode === "custom") {
        setVocabularyRefreshKey((key) => key + 1);
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }

  const tiktokenResult = result && "statistics" in result ? result : null;
  const customResult = result && "vocabulary_size" in result ? result : null;

  return (
    <div className="app">
      <Header />
      <TokenizerModeSelector mode={tokenizerMode} onChange={handleModeChange} />
      <h2>Input</h2>
      <InputModeSelector mode={inputMode} onChange={setInputMode} />
      {tokenizerMode === "tiktokenizer" && (
        <EncodingSelector encodings={encodings} value={encoding} onChange={setEncoding} />
      )}
      {inputMode === "text" ? (
        <TextInput value={text} onChange={setText} />
      ) : (
        <FileUploader accept={inputMode === "txt" ? ".txt" : ".pdf"} onChange={setFile} />
      )}
      <TokenizeButton onClick={handleTokenize} loading={loading} />

      {loading && <LoadingState />}
      {error && <ErrorMessage errorCode={error.error_code} detail={error.detail} />}

      {tiktokenResult && (
        <>
          <h2>Statistics</h2>
          <StatisticsPanel stats={tiktokenResult.statistics} />
          <h2>Tokenized Output</h2>
          <TokenVisualization tokens={tiktokenResult.tokens} />
        </>
      )}

      {customResult && (
        <>
          <h2>Statistics</h2>
          <StatisticsPanel
            stats={{
              character_count: customResult.character_count,
              word_count: customResult.word_count,
              token_count: customResult.token_count,
              tokens_per_word: customResult.tokens_per_word,
              tokens_per_character: customResult.tokens_per_character,
            }}
            vocabularySize={customResult.vocabulary_size}
            newTokenCount={customResult.new_token_count}
          />
          <h2>Tokenized Output</h2>
          <TokenVisualization tokens={customResult.tokens} />
        </>
      )}

      {tokenizerMode === "custom" && (
        <VocabularyPanel sessionId={sessionId} refreshKey={vocabularyRefreshKey} />
      )}
    </div>
  );
}

export default App;
