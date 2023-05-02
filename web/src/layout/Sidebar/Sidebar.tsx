import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import theme from "../../theme/theme";
import { SidebarMenu } from "./menu.constants";
import { SidebarBtn } from "./Components";
import { Stack } from "@mui/material";
import useUser from "../../hooks/useUser";
import useAuth from "../../hooks/useAuth";

const drawerWidth = 240;

export default function Sidebar() {
  const user = useUser();
  const { handleLogout } = useAuth();
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
          sx={{ flexGrow: 1, ml: 2 }}
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
          <SidebarBtn item={item} key={item.id} />
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
            <Stack
              sx={{
                cursor: "pointer",
                borderRadius: "6px",
                padding: "8px 16px",
                "&:hover": {
                  backgroundColor: "rgba(143, 143, 143, 0.13)",
                },
              }}
            >
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 500,
                }}
              >
                {user.name}
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 500,
                }}
              >
                {user.email}
              </Typography>
            </Stack>
          </Stack>
        </List>
        <List onClick={() => handleLogout()}>
          <SidebarBtn item={{ label: "Logout", path: "/logout" }} />
        </List>
      </Stack>
    </Drawer>
  );
}
