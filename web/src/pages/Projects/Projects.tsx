import React from "react";
import { PrivateContainer } from "../../components/Containers";
import { projects_icon } from "../../assets/icons/svg";

export default function Projects() {
  return (
    <PrivateContainer title="Projects" icon={projects_icon}>
      <h1>Projects</h1>
    </PrivateContainer>
  );
}
