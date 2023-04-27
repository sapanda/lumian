import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  SvgIcon,
} from "@mui/material";
import theme from "../../../../theme/theme";

interface SvgProps {
  width?: number;
  height?: number;
  color?: string;
  isActive?: boolean;
}
interface SidebarBtnProps {
  item: {
    label: string;
    icon: (props: SvgProps) => JSX.Element;
    path: string;
  };
}
export default function SidebarBtn(props: SidebarBtnProps) {
  const { item } = props;
  const isActive = item.path === window.location.pathname;
  return (
    <ListItem>
      <ListItemButton
        sx={{
          borderRadius: "6px",
          "&:hover": {
            backgroundColor: isActive
              ? theme.palette.primary.dark
              : "rgba(143, 143, 143, 0.13)",
          },
          ...(isActive && {
            backgroundColor: theme.palette.primary.main,
            "& .MuiListItemIcon-root": {
              color: theme.palette.primary.contrastText,
            },
            "& .MuiListItemText-root": {
              color: theme.palette.primary.contrastText,
            },
          }),
        }}
      >
        <ListItemIcon>
          <SvgIcon component={item.icon} />
        </ListItemIcon>
        <ListItemText primary={item.label} />
      </ListItemButton>
    </ListItem>
  );
}
