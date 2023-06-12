interface answerType {
  text: string;
  references: [number, number][];
}

interface AnswerBoxProps {
  answer: answerType[];
  handleSummaryItemClick?: (
    references: [number, number][],
    index: number
  ) => void;
  selectedIndex?: number | null | undefined;
  queryIndex?: number;
}

export default function AnswerBox(props: AnswerBoxProps) {
  const { answer, handleSummaryItemClick, selectedIndex, queryIndex } = props;
  return (
    <div
      className="h-full px-4 py-[10px] w-[80%]"
      style={{
        boxShadow: "0px 0px 6px rgba(0, 0, 0, 0.25)",
        borderRadius: "10px",
      }}
    >
      {answer.map((item, index) => {
        const regex = /^[a-zA-Z0-9]/;
        let selectedBgColor = "";

        const answerIndex = queryIndex
          ? parseInt(`${queryIndex}${index}`)
          : index;

        if (selectedIndex === answerIndex && item.references.length > 0) {
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
                  handleSummaryItemClick &&
                  handleSummaryItemClick(item.references, answerIndex)
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
            className={`${
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
  );
}
