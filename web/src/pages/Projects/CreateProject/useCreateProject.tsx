import { useCallback, useEffect, useState } from "react";
import { baseApiUrl, projectEndpoints } from "../../../api/apiEndpoints";
import { useNavigate, useParams } from "react-router-dom";
import { PROJECTS } from "../../../router/routes.constant";

const initialState = {
  projectName: "",
  goal: "",
  questions: "",
};

const initialErrors = {
  projectName: "",
  goal: "",
  questions: "",
};

interface IState {
  projectName: string;
  goal: string;
  questions: string;
}

export default function useCreateProject() {
  const [state, setState] = useState<IState>(initialState);
  const [errors, setErrors] = useState<IState>(initialErrors);
  const navigate = useNavigate();

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

    let url = baseApiUrl + projectEndpoints.projectList;
    let method = "POST";
    let updateType = "Added";

    if (projectId) {
      url =
        baseApiUrl +
        projectEndpoints.projectDetail.replace(":projectId", `${projectId}`);
      method = "PATCH";
      updateType = "Updated";
    }

    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (data) {
      alert(`Project ${updateType} Successfully`);
      navigate(PROJECTS.default);
    }
  }

  const getProjectDetail = useCallback(async () => {
    if (!projectId) {
      return;
    }
    const res = await fetch(
      baseApiUrl +
        projectEndpoints.projectDetail.replace(":projectId", `${projectId}`),
      {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Token " + localStorage.getItem("token"),
        },
      }
    );

    const data = await res.json();
    if (data) {
      setState({
        projectName: data.title,
        goal: data.goal,
        questions: data.questions.join("\n"),
      });
    }
  }, [projectId]);

  useEffect(() => {
    getProjectDetail();
  }, [getProjectDetail]);

  return { state, handleChange, handleSave, errors, projectId };
}
