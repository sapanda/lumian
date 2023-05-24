import { Stack } from "@mui/material";

interface QuestionBoxProps {
  question: string;
}

export default function QuestionBox(props: QuestionBoxProps) {
  const { question } = props;
  return (
    <Stack alignItems="flex-end">
      <Stack
        sx={{
          flexDirection: "row",
          gap: "20px",
          padding: "10px 15px",
          background: "#58A0E2",
          color: "white",
          boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.25)",
          borderRadius: "10px",
          height: "100%",
          width: "max-content",
          maxWidth: "80%",
        }}
      >
        {question}
      </Stack>
    </Stack>
  );
}
