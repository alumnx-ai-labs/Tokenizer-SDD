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
import CustomTokenizerSubModeSelector, {
  type CustomTokenizerSubMode,
} from "./components/CustomTokenizerSubModeSelector";
import BpeTrainingForm from "./components/BpeTrainingForm";
import BpeTrainingResult from "./components/BpeTrainingResult";
import BpeTokenizePanel from "./components/BpeTokenizePanel";
import { useSessionId } from "./hooks/useSessionId";
import {
  ApiError,
  bpeTokenizeText,
  getEncodings,
  tokenizeFile,
  tokenizeText,
  trainBpe,
} from "./api/client";
import type {
  BpeTokenizeResult,
  BpeTrainResponse,
  SupportedEncoding,
  TokenizationResult,
} from "./types/api";

function App() {
  const sessionId = useSessionId();
  const [tokenizerMode, setTokenizerMode] = useState<TokenizerMode>("tiktokenizer");
  const [inputMode, setInputMode] = useState<InputMode>("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [encodings, setEncodings] = useState<SupportedEncoding[]>([]);
  const [encoding, setEncoding] = useState<SupportedEncoding>("cl100k_base");
  const [result, setResult] = useState<TokenizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [customSubMode, setCustomSubMode] = useState<CustomTokenizerSubMode>("train-bpe");
  const [bpeTrainResult, setBpeTrainResult] = useState<BpeTrainResponse | null>(null);
  const [bpeTokenizeResult, setBpeTokenizeResult] = useState<BpeTokenizeResult | null>(null);
  const [bpeLoading, setBpeLoading] = useState(false);
  const [bpeError, setBpeError] = useState<ApiError | null>(null);

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
      let response: TokenizationResult;
      if (inputMode === "text") {
        response = await tokenizeText(text, encoding);
      } else if (file) {
        response = await tokenizeFile(file, encoding);
      } else {
        return;
      }
      setResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleTrainBpe(trainingText: string, vocabSize: number) {
    setBpeLoading(true);
    setBpeError(null);
    try {
      const response = await trainBpe(sessionId, trainingText, vocabSize);
      setBpeTrainResult(response);
      setBpeTokenizeResult(null);
    } catch (err) {
      if (err instanceof ApiError) {
        setBpeError(err);
      }
    } finally {
      setBpeLoading(false);
    }
  }

  async function handleBpeTokenize(text: string) {
    setBpeLoading(true);
    setBpeError(null);
    try {
      const response = await bpeTokenizeText(sessionId, text);
      setBpeTokenizeResult(response);
    } catch (err) {
      if (err instanceof ApiError) {
        setBpeError(err);
      }
    } finally {
      setBpeLoading(false);
    }
  }

  function handleCustomSubModeChange(mode: CustomTokenizerSubMode) {
    setCustomSubMode(mode);
    setBpeError(null);
  }

  return (
    <div className="app">
      <Header />
      <TokenizerModeSelector mode={tokenizerMode} onChange={handleModeChange} />

      {tokenizerMode === "tiktokenizer" && (
        <>
          <h2>Input</h2>
          <InputModeSelector mode={inputMode} onChange={setInputMode} />
          <EncodingSelector encodings={encodings} value={encoding} onChange={setEncoding} />
          {inputMode === "text" ? (
            <TextInput value={text} onChange={setText} />
          ) : (
            <FileUploader accept={inputMode === "txt" ? ".txt" : ".pdf"} onChange={setFile} />
          )}
          <TokenizeButton onClick={handleTokenize} loading={loading} />

          {loading && <LoadingState />}
          {error && <ErrorMessage errorCode={error.error_code} detail={error.detail} />}

          {result && (
            <>
              <h2>Statistics</h2>
              <StatisticsPanel stats={result.statistics} />
              <h2>Tokenized Output</h2>
              <TokenVisualization tokens={result.tokens} />
            </>
          )}
        </>
      )}

      {tokenizerMode === "custom" && (
        <CustomTokenizerSubModeSelector mode={customSubMode} onChange={handleCustomSubModeChange} />
      )}

      {tokenizerMode === "custom" && customSubMode === "train-bpe" && (
        <>
          <h2>Train BPE</h2>
          <BpeTrainingForm loading={bpeLoading} onSubmit={handleTrainBpe} />
          {bpeLoading && <LoadingState />}
          {bpeError && <ErrorMessage errorCode={bpeError.error_code} detail={bpeError.detail} />}
          <BpeTrainingResult result={bpeTrainResult} />
        </>
      )}

      {tokenizerMode === "custom" && customSubMode === "tokenize-bpe" && (
        <>
          <h2>Tokenize with BPE</h2>
          <BpeTokenizePanel
            hasTrainedModel={bpeTrainResult !== null}
            loading={bpeLoading}
            onSubmit={handleBpeTokenize}
          />
          {bpeLoading && <LoadingState />}
          {bpeError && <ErrorMessage errorCode={bpeError.error_code} detail={bpeError.detail} />}
          {bpeTokenizeResult && (
            <>
              <h2>Statistics</h2>
              <StatisticsPanel
                stats={{
                  character_count: bpeTokenizeResult.character_count,
                  word_count: bpeTokenizeResult.word_count,
                  token_count: bpeTokenizeResult.token_count,
                  tokens_per_word: bpeTokenizeResult.tokens_per_word,
                  tokens_per_character: bpeTokenizeResult.tokens_per_character,
                }}
              />
              <h2>Tokenized Output</h2>
              <TokenVisualization tokens={bpeTokenizeResult.tokens} />
            </>
          )}
        </>
      )}
    </div>
  );
}

export default App;
