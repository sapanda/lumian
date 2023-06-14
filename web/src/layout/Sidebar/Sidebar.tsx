import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import theme from "../../theme/theme";
import { SidebarMenu } from "./menu.constants";
import { AccountMenu, SidebarBtn } from "./Components";
import { Stack } from "@mui/material";
import { useNavigate } from "react-router-dom";

const drawerWidth = 180;

export default function Sidebar() {
  const navigate = useNavigate();

  return (
    <Drawer
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        "& .MuiDrawer-paper": {
          width: drawerWidth,
          boxSizing: "border-box",
          background: "#051D34",
          color: theme.palette.primary.contrastText,
          padding: "0 12px",
        },
      }}
      variant="permanent"
      anchor="left"
    >
      <Toolbar
        sx={{
          padding: "18px 0!important",
        }}
      >
        <img src="/lumian.svg" alt="Lumian" />
        <Typography
          variant="h4"
          noWrap
          component="div"
          sx={{ flexGrow: 1, ml: 2, color: theme.palette.primary.contrastText }}
        >
          Lumian
        </Typography>
      </Toolbar>
      <Divider
        sx={{
          backgroundColor: theme.palette.primary.light,
        }}
      />
      <List
        sx={{
          marginTop: "22px",
        }}
      >
        {SidebarMenu.map((item) => (
          <SidebarBtn
            item={item}
            key={item.id}
            onClick={() => navigate(item.path)}
          />
        ))}
      </List>
      <Divider
        sx={{
          marginTop: "22px",
          backgroundColor: theme.palette.primary.light,
        }}
      />

      <Stack
        sx={{
          flex: 1,
          height: "100%",
          justifyContent: "flex-end",
        }}
      >
        <List>
          <Stack>
            <AccountMenu />
          </Stack>
        </List>
      </Stack>
    </Drawer>
  );
}
