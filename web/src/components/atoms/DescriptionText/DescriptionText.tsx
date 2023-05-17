interface DescriptionTextProps {
  children?: React.ReactNode;
}
export default function DescriptionText({ children }: DescriptionTextProps) {
  return (
    <span className="text-12-400 text-gray-500">
      <i>{children}</i>
    </span>
  );
}
