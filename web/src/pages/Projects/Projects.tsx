import { PrivateContainer } from "../../components/Containers";
import { projects_icon } from "../../assets/icons/svg";
import { GetStarted } from "./Components";

export default function Projects() {
  return (
    <PrivateContainer title="Projects" icon={projects_icon}>
      <GetStarted />
    </PrivateContainer>
  );
}
