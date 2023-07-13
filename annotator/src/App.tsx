import { useEffect, useState } from "react";

import DiffMatchPatch from "diff-match-patch";
import "./App.css";
import { Button, IconButton, TextField } from "@mui/material";
import { ArrowBack, ArrowForward, PlayArrow } from "@mui/icons-material";

function App() {
  const [data, setData] = useState<any[]>(
    localStorage.getItem("data")
      ? JSON.parse(localStorage.getItem("data") as string)
      : []
  );
  const [currItemIdx, setCurrItemIdx] = useState<number>(0);
  const [showDiff, setShowDiff] = useState<boolean>(true);

  function readFile(file?: File) {
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = (e) => {
      const text = e.target?.result;
      // json
      const json = JSON.parse(text as string);
      setData(json);
    };
    reader.readAsText(file);
  }

  function returnDiffHtml() {
    // diff-match-patch
    if (!data[currItemIdx]) return;

    const billText = data[currItemIdx].bill_text;
    const lawText = data[currItemIdx].law_text;
    const dmp = new DiffMatchPatch();
    const diff = dmp.diff_main(billText, lawText);
    return dmp.diff_prettyHtml(diff);
  }

  function commitChanges() {
    // data to localStorage
    const dataString = JSON.stringify(data);
    localStorage.setItem("data", dataString);
  }

  function handleSubmitChanges(annotation: string) {
    setData((prev) => {
      const newData = [...prev];
      newData[currItemIdx].annotation = annotation;
      return newData;
    });
  }

  function reset() {
    setData([]);
    localStorage.removeItem("data");
    setCurrItemIdx(0);
  }

  function download() {
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(data));
    const dlAnchorElem = document.createElement("a");
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "data.json");
    dlAnchorElem.click();
  }

  useEffect(() => {
    commitChanges();
  }, [data]);

  const currItem = data[currItemIdx];
  return (
    <div className="App mt-10">
      {data.length == 0 ? (
        <input
          className="mb-10"
          type="file"
          onChange={(e) => readFile(e.target?.files?.[0])}
          accept=".json"
        />
      ) : (
        <div>
          <Button color="warning" variant="outlined" onClick={reset}>
            Delete Data
          </Button>
          <span> </span>
          <Button color="warning" variant="contained" onClick={download}>
            Download Data
          </Button>
        </div>
      )}
      <div>
        <h1>
          {showDiff ? "Diff" : "Text"} {currItemIdx + 1}/{data.length}
        </h1>
      </div>
      <div className="navbar">
        {/* Back Button */}
        <IconButton
          onClick={() => setCurrItemIdx(currItemIdx - 1)}
          disabled={currItemIdx <= 0 || !currItem}
        >
          <ArrowBack />
        </IconButton>

        <IconButton
          onClick={() => setCurrItemIdx(currItemIdx + 1)}
          disabled={currItemIdx >= data.length || !currItem}
        >
          <ArrowForward />
        </IconButton>
      </div>
      <div onDoubleClick={() => setShowDiff(!showDiff)}>
        {!showDiff ? (
          <div className="grid grid-cols-2">
            <div>
              <div className="font-bold">Bill</div>
              <div>{currItem?.bill_text}</div>
            </div>
            <div>
              <div className="font-bold">Law</div>
              <div>{currItem?.law_text}</div>
            </div>
          </div>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: returnDiffHtml() }} />
        )}
        <div className="infobar grid grid-cols-2">
          <div>
            <div>Paper</div>
            <div>BOW-OL</div>
            <div>Truth</div>
          </div>
          <div>
            <div> {currItem?.bert_paper}</div>
            <div> {currItem?.pos_bow_bigrams_lemma.toFixed(2)}</div>
            <div> {currItem?.label}</div>
          </div>
        </div>
      </div>
      <div className="input">
      
        <TextField
          autoFocus
          multiline
          placeholder="Annotieren"
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              setCurrItemIdx(currItemIdx + 1);
            }
          }}
          value={currItem?.annotation || ""}
          InputProps={{
            endAdornment: (
              <IconButton onClick={() => setCurrItemIdx(currItemIdx + 1)}>
                <PlayArrow />
              </IconButton>
            ),
          }}
          onChange={(event) => handleSubmitChanges(event.target.value)}
        />
      </div>
    </div>
  );
}

export default App;
