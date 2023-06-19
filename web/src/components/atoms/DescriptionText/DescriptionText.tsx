interface DescriptionTextProps {
  children?: React.ReactNode;
}
export default function DescriptionText({ children }: DescriptionTextProps) {
  return (
    <span
      className="text-gray-500 text-12-400"
      style={{
        marginTop: "0",
      }}
    >
      <i>{children}</i>
    </span>
  );
}
