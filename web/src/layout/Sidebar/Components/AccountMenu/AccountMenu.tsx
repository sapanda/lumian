import React, { useState } from "react";
import Box from "@mui/material/Box";
import Menu from "@mui/material/Menu";

import Divider from "@mui/material/Divider";
import IconButton from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";

import { Stack } from "@mui/material";
import useAuth from "../../../../hooks/useAuth";
import { SidebarBtn } from "..";
import { useNavigate } from "react-router-dom";
import { ACCOUNT_SETTINGS } from "../../../../router/routes.constant";
import theme from "../../../../theme/theme";
import { useGetMeQuery } from "../../../../api/userApi";
import { navigate_next__icon } from "../../../../assets/icons/svg";

export const AccountMenu = () => {
  const navigate = useNavigate();
  const { handleLogout } = useAuth();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const open = Boolean(anchorEl);
  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };
  const handleClose = () => {
    setAnchorEl(null);
  };

  const { data: user } = useGetMeQuery();
  return (
    <React.Fragment>
      <Divider
        sx={{
          marginBottom: "16px",
          backgroundColor: theme.palette.primary.light,
        }}
      />
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          cursor: "pointer",
          borderRadius: "4px",
          padding: "8px",
          maxWidth: "154px",
          "&:hover": {
            backgroundColor: "rgba(143, 143, 143, 0.13)",
          },
        }}
        onClick={handleClick}
      >
        <Stack>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 500,
              color: theme.palette.primary.contrastText,
              maxWidth: "150px",
            }}
          >
            {user?.name}
          </Typography>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 500,
              color: theme.palette.primary.contrastText,
              maxWidth: "150px",
              wordBreak: "break-all",
            }}
          >
            {user?.email}
          </Typography>
        </Stack>
        <Tooltip title="Account settings">
          <IconButton
            size="small"
            sx={{
              ml: 2,
              height: "10px",
              width: "10px",
              padding: "0px",
              marginLeft: "0!important",
              "& svg": {
                width: "10px",
                height: "10px",
              },
            }}
            aria-controls={open ? "account-menu" : undefined}
            aria-haspopup="true"
            aria-expanded={open ? "true" : undefined}
          >
            <img src={navigate_next__icon} alt="navigate_next" />
          </IconButton>
        </Tooltip>
      </Box>
      <Menu
        sx={{
          "& .MuiMenu-paper": {
            width: "200px",
          },
        }}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "right",
        }}
        anchorEl={anchorEl}
        id="account-menu"
        open={open}
        onClose={handleClose}
        onClick={handleClose}
        PaperProps={{
          elevation: 0,
          sx: {
            overflow: "visible",
            filter: "drop-shadow(0px 2px 8px rgba(0,0,0,0.32))",
            mt: 1.5,
            "& .MuiAvatar-root": {
              width: 32,
              height: 32,
              ml: -0.5,
              mr: 1,
            },
            "&:before": {
              content: '""',
              display: "block",
              position: "absolute",
              top: 0,
              right: 14,
              width: 10,
              height: 10,
              bgcolor: "background.paper",
              zIndex: 0,
            },
          },
        }}
      >
        <SidebarBtn
          item={{
            label: "Account",
            path: "/account",
          }}
          onClick={() => {
            handleClose();
            navigate(ACCOUNT_SETTINGS);
          }}
          isBackgroundWhite={true}
        />

        <Divider />
        <SidebarBtn
          item={{
            label: "Logout",
            path: "/account",
          }}
          onClick={() => {
            handleClose();
            handleLogout();
          }}
          isBackgroundWhite={true}
        />
      </Menu>
    </React.Fragment>
  );
};
export default AccountMenu;
