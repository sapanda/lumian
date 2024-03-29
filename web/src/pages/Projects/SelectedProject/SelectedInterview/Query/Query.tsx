import { CircularProgress, Paper, Stack } from "@mui/material";
import theme from "../../../../../theme/theme";

import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import QuestionBox from "./QuestionBox/QuestionBox";
import AnswerBox from "./AnswerBox/AnswerBox";
import { ChatLoader, QueryInput } from "../../../../../components/atoms";
import useInterview from "../useInterview";
import { useEffect } from "react";

interface answerType {
  text: string;
  references: [number, number][];
}
interface queryProps {
  query: string;
  output: answerType[];
}
export default function Query() {
  const {
    conversation,
    citationsCount,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
    userQueryText,
    setUserQueryText,
    query,
    handleSummaryItemClick,
    selectedIndex,
    askQuery,
    isAsking,
  } = useInterview();

  useEffect(() => {
    const element = document.getElementById("questions-container");
    if (element) {
      element.scrollTop = element.scrollHeight;
    }
  }, [query, isAsking]);
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
          display: "flex",
          flexDirection: "column",
          padding: "1rem",
          height: "100%",
          minWidth: "45%",
          gap: "8px",
          minHeight: "75vh",
          maxHeight: "75vh",
        }}
      >
        {!query?.data || query.status !== 201 ? (
          <div className="flex items-center gap-5">
            <CircularProgress />
            <span className="italic text-gray-500 text-12-400">
              Querying will be available in a few minutes...
            </span>
          </div>
        ) : (
          <>
            <div
              className="flex flex-col flex-1 w-full gap-4 p-2 overflow-y-auto"
              id="questions-container"
            >
              <AnswerBox
                answer={[
                  {
                    text: "What would you like to ask?",
                    references: [],
                  },
                ]}
              />
              {query?.data?.map((item: queryProps, index: number) => {
                return (
                  <Stack
                    sx={{
                      gap: "15px",
                    }}
                  >
                    <QuestionBox question={item.query} />
                    <AnswerBox
                      answer={item.output}
                      handleSummaryItemClick={handleSummaryItemClick}
                      selectedIndex={selectedIndex}
                      queryIndex={index}
                    />
                  </Stack>
                );
              })}
              {isAsking && (
                <div className="flex w-full">
                  <ChatLoader />
                </div>
              )}
            </div>
            <div className="flex flex-col w-full p-2">
              <QueryInput
                placeholder="Enter your query"
                onChange={(e) => {
                  setUserQueryText(e.target.value);
                }}
                value={userQueryText}
                onSend={() => {
                  askQuery();
                }}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    askQuery();
                  }
                }}
              />
            </div>
          </>
        )}
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
          style={{
            height: "100%",
            overflowY: "auto",
          }}
        />
      </Paper>
    </Stack>
  );
}
