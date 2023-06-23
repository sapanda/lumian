import { Button } from "@mui/material";
import {
  google_calendar__icon,
  integrations__icon,
  outlook_calendar__icon,
} from "../../assets/icons/svg";
import { PrivateContainer } from "../../components/Containers";
import { PrivateAppbar } from "../../layout";
import { useCalendarStatusQuery } from "../../api/meetingApi";

interface IntegrationAppCardProps {
  name: string;
  icon: string;
  desc: string;
  status: string;
}

interface StatusMapType {
  [key: string]: string;
}
interface BtnVariantMapType {
  [key: string]: {
    variant: "text" | "contained";
    color: "primary" | "error";
    disabled?: boolean;
  };
}
const STATUS_MAP: StatusMapType = {
  "1": "Disconnect",
  "0": "Connect",
  "-1": "Coming Soon",
};

const BTN_VARIANT_MAP: BtnVariantMapType = {
  "1": { variant: "text", color: "error" },
  "0": { variant: "contained", color: "primary" },
  "-1": { variant: "contained", color: "primary", disabled: true },
};
const IntegrationAppCard = (props: IntegrationAppCardProps) => {
  const { name, icon, desc, status } = props;
  return (
    <div className="flex flex-col p-6 min-w-[180px] max-w-[180px] rounded-lg border border-[#CFCECE] max-h-[330px] justify-center gap-6">
      <img src={icon} alt={name} className="w-full h-full" />
      <div className="flex flex-col gap-2">
        <p className="text-12-700">{name}</p>
        <p className="text-12-400">{desc}</p>
      </div>
      <Button
        className="mt-auto"
        variant={BTN_VARIANT_MAP[status].variant}
        color={BTN_VARIANT_MAP[status].color}
        disabled={BTN_VARIANT_MAP[status].disabled}
      >
        {STATUS_MAP[status]}
      </Button>
    </div>
  );
};

export default function Integrations() {
  const { status } = useCalendarStatusQuery();
  const integrations = [
    {
      name: "Google Calendar",
      icon: google_calendar__icon,
      desc: "Instantly connect to meetings on your calendar",
      status: status === "success" ? "1" : "0",
    },
    {
      name: "Outlook Calendar",
      icon: outlook_calendar__icon,
      desc: "Instantly connect to meetings on your calendar",
      status: "-1",
    },
  ];
  return (
    <PrivateContainer
      appBar={<PrivateAppbar title="Integrations" icon={integrations__icon} />}
    >
      <div className="flex justify-center w-full h-full mt-[10%] gap-12">
        {integrations.map((integration, index) => (
          <IntegrationAppCard key={index} {...integration} />
        ))}
      </div>
    </PrivateContainer>
  );
}
