import { CircularProgress, Paper } from "@mui/material";
import theme from "../../../../../theme/theme";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import useInterview from "../useInterview";

interface conciseProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

export default function Concise() {
  const {
    concise,
    conversation,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useInterview();
  return (
    <div className="flex gap-5 px-8 py-4">
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
        {!concise ? (
          <div className="flex items-center gap-5">
            <CircularProgress />
            <span className="italic text-gray-500 text-12-400">
              Concise transcript generation will take a few minutes...
            </span>
          </div>
        ) : (
          <div className="overflow-y-auto">
            {concise?.map((item: conciseProps, index: number) => {
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
                      className={`${
                        item?.references?.length > 0 && "hover:bg-blue-100"
                      } cursor-pointer ${selectedBgColor}`}
                      onClick={() =>
                        item?.references?.length > 0 &&
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
                    className={`${
                      item?.references?.length > 0 && "hover:bg-blue-100"
                    } cursor-pointer ${selectedBgColor}`}
                    onClick={() =>
                      item?.references?.length > 0 &&
                      handleSummaryItemClick(item.references, index)
                    }
                  >
                    {item.text}
                  </span>
                  <br />
                  <br />
                </>
              );
            })}
          </div>
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
          className="h-full overflow-y-auto"
          ref={transcriptRef}
          dangerouslySetInnerHTML={{ __html: conversation }}
        />
      </Paper>
    </div>
  );
}
