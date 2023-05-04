import React, { useEffect } from "react";
import ButtonGroup from "@mui/material/ButtonGroup";
import Button from "@mui/material/Button";
import theme from "../../../theme/theme";

//JS docs
/**
 * @param {Object} props
 * @param {Array} props.tabs
 * @param {String} props.tabs.name
 * @param {JSX.Element} props.tabs.component
 * @param {Number} props.activeTabIndex
 * @param {Function} props.onTabChange
 * @returns {JSX.Element}
 * @constructor
 * @example
 * <TabNav tabs={[{name:"Tab 1", component:<Tab1/>}, {name:"Tab 2", component:<Tab2/>]} activeTabIndex={0} />
 */

interface TabNavProps {
  tabs: {
    name: string;
    component: JSX.Element;
  }[];
  activeTabIndex?: number;
  disableInactiveTabs?: boolean;
  onTabChange?: (index: number) => void;
  disabledTabsIndex?: number[];
  buttonStyles?: React.CSSProperties;
}

export default function TabNav(props: TabNavProps) {
  const {
    tabs = [],
    activeTabIndex = 0,
    disableInactiveTabs = false,
    onTabChange,
    disabledTabsIndex = [],
    buttonStyles = {},
  } = props;

  const [activeTab, setActiveTab] = React.useState(
    activeTabIndex > tabs?.length ? 0 : activeTabIndex
  );

  function handleTabChange(index: number) {
    setActiveTab(index);
    onTabChange && onTabChange(index);
  }

  useEffect(() => {
    setActiveTab(activeTabIndex);
  }, [activeTabIndex]);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
      <ButtonGroup
        disableElevation
        aria-label="Disabled elevation buttons"
        sx={{
          borderBottom: "2px solid #F0F0F0",
          gap: "8px",
          padding: "0 40px",
        }}
      >
        {tabs.map((tab, index) => (
          <div
            style={{
              paddingBottom: "6px",
              paddingTop: "18px",
              ...(activeTab === index && {
                borderBottom: `2px solid ${theme.palette.primary.main}`,
              }),
            }}
          >
            <Button
              key={index}
              onClick={() => handleTabChange(index)}
              variant={activeTab === index ? "contained" : "text"}
              sx={{
                fontSize: "14px",
                fontWeight: 400,
                backgroundColor:
                  activeTab === index
                    ? theme.palette.primary.main
                    : theme.palette.common.white,
                color:
                  activeTab === index
                    ? theme.palette.common.white
                    : theme.palette.common.black,
                "&.MuiButtonGroup-grouped": {
                  borderRadius: "4px!important",
                },

                width: "92px",
                textTransform: "none",
                "&:hover": {
                  color:
                    activeTab === index
                      ? theme.palette.common.white
                      : theme.palette.primary.dark,
                  backgroundColor:
                    activeTab === index
                      ? theme.palette.primary.main
                      : theme.palette.primary.light,
                },
                ...buttonStyles,
              }}
              disabled={
                disableInactiveTabs && disabledTabsIndex?.includes(index)
              }
            >
              {tab.name}
            </Button>
          </div>
        ))}
      </ButtonGroup>
      <div className="tab-nav__content">{tabs[activeTab]?.component}</div>
    </div>
  );
}
