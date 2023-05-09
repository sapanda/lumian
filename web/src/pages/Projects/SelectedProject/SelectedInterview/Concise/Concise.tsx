import { Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";
import useConcise from "./useConcise";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";

interface conciseProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

interface conciseType {
  data: conciseProps[];
  interviewTranscript: string;
}

export default function Concise(props: conciseType) {
  const { data, interviewTranscript } = props;
  const {
    conversation,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useConcise(interviewTranscript);
  return (
    <Stack
      sx={{
        flexDirection: "row",
        gap: "20px",
      }}
    >
      <Paper
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          padding: "1rem",
          height: "100%",
          minHeight: "72.5vh",
          minWidth: "49%",
          maxWidth: "49%",
        }}
      >
        <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
          Concise
        </Typography>
        <div>
          {data.map((item, index) => {
            const regex = /^[a-zA-Z0-9]/;
            if (item.text[0] === " " || !regex.test(item.text[0])) {
              let selectedBgColor = "";
              if (selectedIndex === index) {
                selectedBgColor = "bg-blue-200";
              }
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
                  <br />
                  <br />
                </>
              );
            }

            return (
              <>
                <span
                  key={index}
                  className="hover:bg-blue-100 cursor-pointer"
                  onClick={() => handleSummaryItemClick(item.references, index)}
                >
                  {item.text}
                </span>
                <br />
                <br />
              </>
            );
          })}
        </div>
      </Paper>

      <Paper
        sx={{
          padding: "3.5rem 1rem 1rem 1rem",
          height: "100%",
          minWidth: "49%",
          maxWidth: "49%",
          position: "relative",
        }}
      >
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
        <div
          ref={transcriptRef}
          dangerouslySetInnerHTML={{ __html: conversation }}
          style={{
            height: "63vh",
            overflowY: "auto",
          }}
        />
      </Paper>
    </Stack>
  );
}
