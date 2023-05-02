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

const drawerWidth = 240;

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
        },
      }}
      variant="permanent"
      anchor="left"
    >
      <Toolbar>
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
          margin: "0 16px",
        }}
      />
      <List>
        {SidebarMenu.map((item) => (
          <SidebarBtn
            item={item}
            key={item.id}
            onClick={() => navigate(item.path)}
          />
        ))}
      </List>
      <Divider />

      <Stack
        sx={{
          flex: 1,
          height: "100%",
          justifyContent: "flex-end",
        }}
      >
        <List>
          <Stack
            sx={{
              padding: "8px 16px",
            }}
          >
            <AccountMenu />
          </Stack>
        </List>
      </Stack>
    </Drawer>
  );
}
