import { AppBar, IconButton, Stack, Toolbar, Typography } from "@mui/material";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const drawerWidth = 180;

interface PrivateAppbarProps {
  breadcrumb?: {
    title: string;
    path: string;
  };
  icon: string;
  title: string;
  children?: React.ReactNode;
  isTitleEditable?: boolean;
  onEditEnd?: (title: string) => void;
}

function AppBarLabel(
  icon: string,
  title: string,
  breadcrumb?: {
    title: string;
    path: string;
  },
  isTitleEditable?: boolean,
  onEditEnd?: (title: string) => void
) {
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(title);

  useEffect(() => {
    setEditTitle(title);
  }, [title]);
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
          {isEditing ? (
            <input
              type="text"
              value={editTitle}
              onChange={(e) => {
                setEditTitle(e.target.value);
              }}
              onBlur={() => {
                onEditEnd && onEditEnd(editTitle);
                setIsEditing(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  onEditEnd && onEditEnd(editTitle);
                  setIsEditing(false);
                }
              }}
              style={{
                border: "#E5E5E5 1px solid",
                outline: "none",
                color: "black",
                padding: "4px",
                minWidth: "max-content",
              }}
              className="text-20-700"
            />
          ) : (
            <Typography
              variant="h2"
              noWrap
              component="div"
              sx={{ flexGrow: 1 }}
              {...(isTitleEditable && {
                onDoubleClick: () => setIsEditing(true),
              })}
            >
              {title}
            </Typography>
          )}
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
    </Toolbar>
  );
}

export default function PrivateAppbar(props: PrivateAppbarProps) {
  const { children, breadcrumb, icon, title, isTitleEditable, onEditEnd } =
    props;
  return (
    <AppBar
      position="fixed"
      color="inherit"
      sx={{ width: `calc(100% - ${drawerWidth}px)`, ml: `${drawerWidth}px` }}
    >
      <Stack direction="row" gap="20px">
        <Toolbar>
          {AppBarLabel(icon, title, breadcrumb, isTitleEditable, onEditEnd)}
        </Toolbar>
        {!!children && children}
      </Stack>
    </AppBar>
  );
}
