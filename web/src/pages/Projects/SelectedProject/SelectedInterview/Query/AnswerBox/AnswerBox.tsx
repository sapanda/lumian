import { Stack } from "@mui/material";

interface answerType {
  text: string;
  references: [number, number][];
}

interface AnswerBoxProps {
  answer: answerType[];
}

export default function AnswerBox(props: AnswerBoxProps) {
  const { answer } = props;
  return (
    <Stack
      sx={{
        flexDirection: "row",
        gap: "20px",
        padding: "10px 15px",
        boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.25)",
        borderRadius: "10px",
        width: "80%",
        height: "100%",
      }}
    >
      {answer.map((item) => {
        return item.text;
      })}
    </Stack>
  );
}
