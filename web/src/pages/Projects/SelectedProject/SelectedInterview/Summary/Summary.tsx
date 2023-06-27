import React, { useState } from "react";
import { CircularProgress, Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import useInterview from "../useInterview";
import {
  copied_toast__icon,
  copy__icon,
} from "../../../../../assets/icons/svg";

interface summaryProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

interface answerType {
  text: string;
  references: [number, number][];
}
interface queryProps {
  query: string;
  output: answerType[];
}
export default function Summary() {
  const [copiedState, setCopiedState] = useState({
    showSummaryCopied: false,
    showQuestionCopied: false,
  });
  const {
    summary,
    conversation,
    questions,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useInterview();

  function onCopyClick(copyType: "summary" | "question") {
    if (copyType === "summary") {
      const element = document.getElementById("summary");
      const innerText = element?.innerText;
      innerText && navigator.clipboard.writeText(innerText);

      setCopiedState({ ...copiedState, showSummaryCopied: true });
      setTimeout(() => {
        setCopiedState({ ...copiedState, showSummaryCopied: false });
      }, 1000);
    } else {
      const element = document.getElementById("questions");
      const innerText = element?.innerText;
      innerText && navigator.clipboard.writeText(innerText);
      setCopiedState({ ...copiedState, showQuestionCopied: true });
      setTimeout(() => {
        setCopiedState({ ...copiedState, showQuestionCopied: false });
      }, 1000);
    }
  }

  return (
    <Stack
      sx={{
        flexDirection: "row",
        gap: "20px",
        padding: "1rem 2rem",
      }}
    >
      <Paper
        sx={{
          minWidth: "49%",
          maxWidth: "49%",
          padding: "1rem",
          maxHeight: "75vh",
          minHeight: "75vh",
        }}
      >
        <div className="flex flex-col overflow-y-auto max-h-[70vh] min-h-[70vh] gap-5">
          <div className="flex">
            <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
              Summary
            </Typography>
            <img
              src={copy__icon}
              alt="copy"
              className="ml-2 cursor-pointer"
              onClick={() => onCopyClick("summary")}
            />
            <img
              src={copied_toast__icon}
              alt="copy"
              className="transition-opacity duration-500 ease-in-out"
              style={{
                opacity: copiedState.showSummaryCopied ? 1 : 0,
              }}
            />
          </div>

          {!summary ? (
            <div className="flex items-center gap-5">
              <CircularProgress />
              <span className="italic text-gray-500 text-12-400">
                Summary generation will take a few minutes...
              </span>
            </div>
          ) : (
            <div id="summary">
              {summary?.map((item: summaryProps, index: number) => {
                const regex = /^[a-zA-Z0-9]/;
                let selectedBgColor = "";
                if (selectedIndex === index) {
                  selectedBgColor = "bg-blue-200";
                }
                if (item.text[0] === " " || !regex.test(item.text[0])) {
                  return (
                    <React.Fragment key={`summary-${index}`}>
                      {item.text[0]}
                      <span
                        key={index}
                        className={`text-12-400 ${
                          item?.references?.length > 0 && "hover:bg-blue-100"
                        } cursor-pointer ${selectedBgColor}`}
                        onClick={() =>
                          item?.references?.length > 0 &&
                          handleSummaryItemClick(item.references, index)
                        }
                      >
                        {item.text.slice(1)}
                      </span>
                    </React.Fragment>
                  );
                }

                return (
                  <span
                    key={index}
                    className={`text-12-400 ${
                      item?.references?.length > 0 && "hover:bg-blue-100"
                    } cursor-pointer ${selectedBgColor}`}
                    onClick={() =>
                      item?.references?.length > 0 &&
                      handleSummaryItemClick(item.references, index)
                    }
                  >
                    {item.text}
                  </span>
                );
              })}
            </div>
          )}

          <div className="flex">
            <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
              Questions
            </Typography>
            <img
              src={copy__icon}
              alt="copy"
              className="mx-2 cursor-pointer"
              onClick={() => onCopyClick("question")}
            />
            <img
              src={copied_toast__icon}
              alt="copy"
              className="transition-opacity duration-500 ease-in-out"
              style={{
                opacity: copiedState.showQuestionCopied ? 1 : 0,
              }}
            />
          </div>

          {questions?.status !== 201 || !questions?.data ? (
            <div className="flex items-center gap-5">
              <CircularProgress />
              <span className="italic text-gray-500 text-12-400">
                Q&A generation will take a few minutes...
              </span>
            </div>
          ) : (
            <div className="flex flex-col gap-4" id="questions">
              {questions?.data?.length > 0 ? (
                questions?.data?.map((item: queryProps, index: number) => {
                  const answer = item?.output;
                  return (
                    <Stack>
                      <span className="italic text-12-700 ">{item?.query}</span>
                      <div>
                        {answer.map((item, queryIndex) => {
                          const regex = /^[a-zA-Z0-9]/;
                          let selectedBgColor = "";

                          const answerIndex = `answer-${index}-${queryIndex}`;

                          if (
                            selectedIndex === answerIndex &&
                            item.references.length > 0
                          ) {
                            selectedBgColor = "bg-blue-200";
                          }
                          if (
                            item.text[0] === " " ||
                            !regex.test(item.text[0])
                          ) {
                            return (
                              <>
                                {item.text[0]}
                                <span
                                  key={index}
                                  className={`text-12-500 ${
                                    item?.references?.length > 0 &&
                                    "hover:bg-blue-100"
                                  } cursor-pointer ${selectedBgColor}`}
                                  onClick={() =>
                                    item?.references?.length > 0 &&
                                    handleSummaryItemClick &&
                                    handleSummaryItemClick(
                                      item.references,
                                      answerIndex
                                    )
                                  }
                                >
                                  {item.text.slice(1)}
                                </span>
                              </>
                            );
                          }

                          return (
                            <span
                              key={index}
                              className={`text-12-500 ${
                                item?.references?.length > 0 &&
                                "hover:bg-blue-100"
                              } cursor-pointer ${selectedBgColor}`}
                              onClick={() =>
                                item.references.length > 0 &&
                                handleSummaryItemClick &&
                                handleSummaryItemClick(
                                  item.references,
                                  answerIndex
                                )
                              }
                            >
                              {item.text}
                            </span>
                          );
                        })}
                      </div>
                    </Stack>
                  );
                })
              ) : (
                <span className="italic text-gray-500 text-12-400">
                  No questions available
                </span>
              )}
            </div>
          )}
        </div>
      </Paper>

      <Paper
        sx={{
          padding: "1rem",
          minWidth: "49%",
          maxWidth: "49%",
          position: "relative",
          ...(citationsCount > 1 && { paddingTop: "3.5rem" }),
          minHeight: "75vh",
          maxHeight: "75vh",
        }}
      >
        {citationsCount > 1 && (
          <div className="absolute top-0 right-0 p-2 m-2 bg-white rounded-md shadow-md">
            <span className="text-primary">{`Citation ${activeCitationIndex} of ${citationsCount}`}</span>
            <KeyboardArrowUp
              sx={{
                color: theme.palette.text.secondary,
                cursor: "pointer",
              }}
              onClick={() => {
                scrollToNextHighlightedText(activeCitationIndex - 2);
              }}
            />
            <KeyboardArrowDown
              sx={{
                color: theme.palette.text.secondary,
                cursor: "pointer",
              }}
              onClick={() => {
                scrollToNextHighlightedText(activeCitationIndex);
              }}
            />
          </div>
        )}
        <div
          ref={transcriptRef}
          dangerouslySetInnerHTML={{ __html: conversation }}
          className="h-full overflow-y-auto"
        />
      </Paper>
    </Stack>
  );
}
