import { Paper, Stack, Typography } from "@mui/material";
import theme from "../../../../../theme/theme";

interface summaryProps {
  text: string;
  [key: string]: string | number | Array<Array<number>>;
}

interface SummaryType {
  data: summaryProps[];
}

export default function Query(props: SummaryType) {
  const { data } = props;
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
          padding: "1rem",
          height: "100%",
          minWidth: "45%",
          gap: "8px",
        }}
      >
        <Typography variant="h5" sx={{ color: theme.palette.common.black }}>
          Query
        </Typography>
        <Stack direction="row">
          {data.map((item, index) => {
            return (
              <span key={index} className="hover:bg-blue-100 cursor-pointer">
                {item.text}
              </span>
            );
          })}
        </Stack>
      </Paper>

      <Paper
        sx={{
          padding: "1rem",
          height: "100%",
          minWidth: "45%",
        }}
      >
        {data.reduce((acc, curr) => {
          return acc + curr.text;
        }, "")}
      </Paper>
    </Stack>
  );
}
