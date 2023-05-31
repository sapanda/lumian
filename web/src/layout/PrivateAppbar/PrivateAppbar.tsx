import {
  AppBar,
  Backdrop,
  CircularProgress,
  IconButton,
  Stack,
  Toolbar,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

const drawerWidth = 240;

interface PrivateAppbarProps {
  breadcrumb?: {
    title: string;
    path: string;
  };
  icon: string;
  title: string;
  children?: React.ReactNode;
}

function AppBarLabel(
  icon: string,
  title: string,
  breadcrumb?: {
    title: string;
    path: string;
  }
) {
  const navigate = useNavigate();
  return (
    <Toolbar>
      <Stack
        sx={{
          flexDirection: "row",
        }}
      >
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ mr: 2, p: 0 }}
        >
          <img src={icon} alt="Projects" />
        </IconButton>
        <Stack>
          <Typography variant="h2" noWrap component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          {!!breadcrumb && breadcrumb.title && (
            <Typography
              variant="h6"
              noWrap
              component="div"
              fontWeight="light"
              sx={{ flexGrow: 1, cursor: "pointer" }}
              onClick={() => navigate(breadcrumb.path)}
            >
              {breadcrumb.title}
            </Typography>
          )}
        </Stack>
      </Stack>
      <Backdrop
        sx={{ zIndex: (theme) => theme.zIndex.drawer + 999 }}
        open={false}
      >
        <CircularProgress color="primary" />
      </Backdrop>
    </Toolbar>
  );
}

export default function PrivateAppbar(props: PrivateAppbarProps) {
  const { children, breadcrumb, icon, title } = props;

  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
    >
      <Stack direction="row" gap="20px">
        <Toolbar>{AppBarLabel(icon, title, breadcrumb)}</Toolbar>
        {!!children && children}
      </Stack>
    </AppBar>
  );
}
