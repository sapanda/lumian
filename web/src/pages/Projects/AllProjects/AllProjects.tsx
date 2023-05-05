import { projects_icon } from "../../../assets/icons/svg";
import { PrivateContainer } from "../../../components/Containers";
import GetStarted from "./GetStarted";

export default function AllProjects() {
  return (
    <PrivateContainer title="Projects" icon={projects_icon}>
      <GetStarted />
    </PrivateContainer>
  );
}
