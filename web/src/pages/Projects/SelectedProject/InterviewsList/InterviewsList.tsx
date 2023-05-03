import { projects_icon } from "../../../../assets/icons/svg";
import { PrivateContainer } from "../../../../components/Containers";
import GetStarted from "./GetStarted/GetStarted";

export default function InterviewsList() {
  return (
    <PrivateContainer title="Project Name" icon={projects_icon}>
      <GetStarted />
    </PrivateContainer>
  );
}
