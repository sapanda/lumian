import { AppBar, IconButton, Stack, Toolbar, Typography } from "@mui/material";

const drawerWidth = 240;

interface PrivateAppbarProps {
  title: string;
  icon: string;
  subtitle?: string;
  children?: React.ReactNode;
}

function appBarLabel(title: string, icon: string, subtitle?: string) {
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
          {!!subtitle && (
            <Typography
              variant="h6"
              noWrap
              component="div"
              sx={{ flexGrow: 1 }}
            >
              {subtitle}
            </Typography>
          )}
        </Stack>
      </Stack>
    </Toolbar>
  );
}

export default function PrivateAppbar(props: PrivateAppbarProps) {
  const { children, title, icon, subtitle } = props;
  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
    >
      <Stack direction="row" gap="20px">
        <Toolbar>{appBarLabel(title, icon, subtitle)}</Toolbar>
        {!!children && children}
      </Stack>
    </AppBar>
  );
}
