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
    icon?: (props: SvgProps) => JSX.Element;
    path: string;
  };
  onClick?: () => void;
  sx?: React.CSSProperties;
  isBackgroundWhite?: boolean;
}
export default function SidebarBtn(props: SidebarBtnProps) {
  const { item, isBackgroundWhite } = props;
  const isActive = item.path === window.location.pathname;

  const nonWhiteBgBtnStyle = {
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
  };
  const whiteBgBtnStyle = {
    "&:hover": {
      backgroundColor: theme.palette.primary.light,
    },
  };
  return (
    <ListItem
      sx={{
        padding: "4px 8px",
      }}
    >
      <ListItemButton
        sx={{
          borderRadius: "6px",
          ...(isBackgroundWhite ? whiteBgBtnStyle : nonWhiteBgBtnStyle),
        }}
      >
        {item.icon && (
          <ListItemIcon>
            <SvgIcon component={item.icon} />
          </ListItemIcon>
        )}
        <ListItemText primary={item.label} />
      </ListItemButton>
    </ListItem>
  );
}
