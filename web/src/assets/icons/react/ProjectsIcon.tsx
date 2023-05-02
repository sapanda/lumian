interface SvgProps {
  width?: number;
  height?: number;
  color?: string;
  isActive?: boolean;
}

const ProjectsIcon = (props: SvgProps) => {
  const fillColor = props.isActive ? "#127FE4" : props.color || "#FAFAFA";
  return (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" {...props}>
      <path
        fill={fillColor}
        fillRule="evenodd"
        d="M.3 4.5A2.7 2.7 0 0 1 3 1.8h10.2a2.7 2.7 0 0 1 2.7 2.7v.3a.9.9 0 0 1-1.8 0v-.3a.9.9 0 0 0-.9-.9H3a.9.9 0 0 0-.9.9v6.6a.9.9 0 0 0 .9.9h.6a.9.9 0 1 1 0 1.8H3a2.7 2.7 0 0 1-2.7-2.7V4.5Z"
        clipRule="evenodd"
      />
      <path
        fill={fillColor}
        fillRule="evenodd"
        d="M6.3 10.8a3.3 3.3 0 0 1 3.3-3.3h10.8a3.3 3.3 0 0 1 3.3 3.3V18a3.3 3.3 0 0 1-3.3 3.3H9.6A3.3 3.3 0 0 1 6.3 18v-7.2Zm3.3-1.5a1.5 1.5 0 0 0-1.5 1.5V18a1.5 1.5 0 0 0 1.5 1.5h10.8a1.5 1.5 0 0 0 1.5-1.5v-7.2a1.5 1.5 0 0 0-1.5-1.5H9.6Z"
        clipRule="evenodd"
      />
      <path
        fill={fillColor}
        d="M12.3 16.18a1.2 1.2 0 0 0 1.817 1.03l2.968-1.781a1.2 1.2 0 0 0 0-2.058l-2.968-1.78a1.2 1.2 0 0 0-1.817 1.028v3.562Z"
      />
    </svg>
  );
};
export default ProjectsIcon;
