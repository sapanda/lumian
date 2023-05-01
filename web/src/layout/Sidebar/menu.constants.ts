import { ProjectsIcon } from "../../assets/icons/react";

interface SvgProps {
  width?: number;
  height?: number;
  color?: string;
  isActive?: boolean;
}
interface SidebarMenuItem {
  id: string;
  label: string;
  icon?: (props: SvgProps) => JSX.Element;
  path: string;
}

export const SidebarMenu: SidebarMenuItem[] = [
  {
    id: "1",
    label: "Projects",
    icon: ProjectsIcon,
    path: "/projects",
  },
];
