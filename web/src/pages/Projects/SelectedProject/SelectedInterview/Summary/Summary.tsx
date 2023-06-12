import { Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";
import { KeyboardArrowDown, KeyboardArrowUp } from "@mui/icons-material";
import useInterview from "../useInterview";

interface summaryProps {
  text: string;
  references: [number, number][];
  [key: string]: string | number | Array<Array<number>>;
}

interface SummaryType {
  data: summaryProps[];
}
interface answerType {
  text: string;
  references: [number, number][];
}
interface queryProps {
  query: string;
  output: answerType[];
}
export default function Summary(props: SummaryType) {
  const { data } = props;
  const {
    conversation,
    questions,
    handleSummaryItemClick,
    citationsCount,
    selectedIndex,
    transcriptRef,
    scrollToNextHighlightedText,
    activeCitationIndex,
  } = useInterview();

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
          <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
            Summary
          </Typography>

          <div>
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
                  </>
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

          <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
            Questions
          </Typography>

          <div className="flex flex-col gap-4">
            {questions?.map((item: queryProps, index: number) => {
              const answer = item?.output;
              return (
                <Stack>
                  <span className="italic text-12-700 ">{item?.query}</span>
                  <div>
                    {answer.map((item, queryIndex) => {
                      const regex = /^[a-zA-Z0-9]/;
                      let selectedBgColor = "";

                      const answerIndex = queryIndex
                        ? parseInt(`${queryIndex}${index}`)
                        : index;
                      if (
                        selectedIndex === answerIndex &&
                        item.references.length > 0
                      ) {
                        selectedBgColor = "bg-blue-200";
                      }
                      if (item.text[0] === " " || !regex.test(item.text[0])) {
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
                            item?.references?.length > 0 && "hover:bg-blue-100"
                          } cursor-pointer ${selectedBgColor}`}
                          onClick={() =>
                            item.references.length > 0 &&
                            handleSummaryItemClick &&
                            handleSummaryItemClick(item.references, index)
                          }
                        >
                          {item.text}
                        </span>
                      );
                    })}
                  </div>
                </Stack>
              );
            })}
          </div>
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
