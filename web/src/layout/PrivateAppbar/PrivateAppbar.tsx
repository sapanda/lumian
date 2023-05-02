import { AppBar, IconButton, Toolbar, Typography } from "@mui/material";

const drawerWidth = 240;

interface PrivateAppbarProps {
  title: string;
  icon: string;
}

function appBarLabel(label: string, icon: string) {
  return (
    <Toolbar>
      <IconButton edge="start" color="inherit" aria-label="menu" sx={{ mr: 2 }}>
        <img src={icon} alt="Projects" />
      </IconButton>
      <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
        {label}
      </Typography>
    </Toolbar>
  );
}

export default function PrivateAppbar(props: PrivateAppbarProps) {
  const { title, icon } = props;
  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
    >
      <Toolbar>{appBarLabel(title, icon)}</Toolbar>
    </AppBar>
  );
}
