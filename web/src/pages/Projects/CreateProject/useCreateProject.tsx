import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import {
  useCreateProjectMutation,
  useGetProjectMutation,
  useUpdateProjectMutation,
} from "../../../api/projectApi";

const initialState = {
  projectName: "",
  goal: "",
  questions: "",
};

const initialErrors = {
  ...initialState,
};

interface IState {
  projectName: string;
  goal: string;
  questions: string;
}

export default function useCreateProject() {
  const { mutateAsync: getProject } = useGetProjectMutation();
  const [state, setState] = useState<IState>(initialState);
  const [errors, setErrors] = useState<IState>(initialErrors);
  const { mutate: createProject } = useCreateProjectMutation();
  const { mutate: updateProject } = useUpdateProjectMutation();

  const { projectId } = useParams();

  function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target;
    setState((prevState) => ({ ...prevState, [name]: value }));
    return;
  }

  function isValidated() {
    const errors = { ...initialErrors };
    if (!state.projectName) {
      errors.projectName = "Project Name is required";
    }
    if (!state.goal) {
      errors.goal = "Goal is required";
    }

    if (!state.questions) {
      errors.questions = "Questions are required";
    }

    setErrors(errors);
    return errors.projectName || errors.goal || errors.questions;
  }
  async function handleSave() {
    if (isValidated()) {
      return;
    }

    const payload = {
      title: state.projectName,
      goal: state.goal,
      questions: state.questions.split("\n").filter((q) => q.length > 0),
    };

    if (projectId) {
      updateProject({ payload, projectId: parseInt(projectId) });
      return;
    }

    createProject(payload);
  }

  const getProjectDetail = useCallback(async () => {
    if (!projectId) {
      return;
    }
    const data = await getProject(parseInt(projectId));

    if (data) {
      setState({
        projectName: data.name,
        goal: data.goal,
        questions: data.questions.join("\n"),
      });
    }
  }, [getProject, projectId]);

  useEffect(() => {
    getProjectDetail();
  }, [getProjectDetail]);

  return { state, handleChange, handleSave, errors, projectId };
}
