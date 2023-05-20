import { Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";
import useSummary from "./useSummary";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";

interface summaryProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

interface SummaryType {
  data: summaryProps[];
  interviewTranscript: string;
}

export default function Summary(props: SummaryType) {
  const { data, interviewTranscript } = props;
  const {
    conversation,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useSummary(interviewTranscript);
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
          gap: "8px",
          padding: "1rem",
          minWidth: "49%",
          maxWidth: "49%",
          minHeight: "75vh",
          maxHeight: "75vh",
        }}
      >
        <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
          Summary
        </Typography>
        
        <div className="min-h-[63vh] max-h-[63vh] overflow-y-auto">
          {data.map((item, index) => {
            const regex = /^[a-zA-Z0-9]/;
            let selectedBgColor = "";
            if (selectedIndex === index) {
              selectedBgColor = "bg-blue-200";
            }
            if (item.text[0] === " " || !regex.test(item.text[0])) {
              return (
                <>
                  {item.text[0]}
                  <span
                    key={index}
                    className={`hover:bg-blue-100 cursor-pointer ${selectedBgColor}`}
                    onClick={() =>
                      handleSummaryItemClick(item.references, index)
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
                className={`hover:bg-blue-100 cursor-pointer ${selectedBgColor}`}
                onClick={() => handleSummaryItemClick(item.references, index)}
              >
                {item.text}
              </span>
            );
          })}
        </div>
      </Paper>

      <Paper
        sx={{
          padding: "1rem",
          minWidth: "49%",
          maxWidth: "49%",
          position: "relative",
          ...(citationsCount > 0 && { paddingTop: "3.5rem" }),
          minHeight: "75vh",
          maxHeight: "75vh",
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
          className="h-full overflow-y-auto"
        />
      </Paper>
    </Stack>
  );
}
