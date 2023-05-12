import { Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";
import useQuery from "./useQuery";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import QuestionBox from "./QuestionBox/QuestionBox";
import AnswerBox from "./AnswerBox/AnswerBox";

interface queryType {
  data: queryProps[];
  interviewTranscript: string;
}
interface answerType {
  text: string;
  references: [number, number][];
}
interface queryProps {
  query: string;
  output: answerType[];
}
export default function Query(props: queryType) {
  const { data, interviewTranscript } = props;
  const {
    conversation,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useQuery(interviewTranscript);

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
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            minHeight: "63vh",
            maxHeight: "63vh",
            overflowY: "auto",
            padding: "2rem",
            gap: "15px",
          }}
        >
          <AnswerBox
            answer={[
              {
                text: "What would you like to ask?",
                references: [],
              },
            ]}
          />
          {data.map((item: queryProps) => {
            return (
              <Stack
                sx={{
                  gap: "15px",
                }}
              >
                <QuestionBox question={item.query} />
                <AnswerBox answer={item.output} />
              </Stack>
            );
          })}
        </div>
      </Paper>

      <Paper
        sx={{
          padding: "1rem",
          height: "100%",
          minWidth: "49%",
          maxWidth: "49%",
          position: "relative",
          ...(citationsCount > 0 && { paddingTop: "3.5rem" }),
        }}
      >
        {citationsCount > 0 && (
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
            minHeight: "63vh",
            maxHeight: "63vh",
            overflowY: "auto",
          }}
        />
      </Paper>
    </Stack>
  );
}
