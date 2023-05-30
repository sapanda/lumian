

interface QuestionBoxProps {
  question: string;
}

export default function QuestionBox(props: QuestionBoxProps) {
  const { question } = props;
  return (
    <div className="flex flex-col items-end">
      <div
        className="flex gap-5 px-4 py-[10px] bg-blue-400 h-full text-white max-w-[80%] w-max"
        style={{
          boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.25)",
          borderRadius: "10px",
        }}
      >
        {question}
      </div>
    </div>
  );
}
