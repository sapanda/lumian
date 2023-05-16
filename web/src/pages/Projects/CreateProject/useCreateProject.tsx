import { useState } from "react";
import { baseApiUrl, userEndPoints } from "../../../api/apiEndpoints";

const initialState = {
  projectName: "",
  goal: "",
  questions: "",
  members: "",
};

const initialErrors = {
  projectName: "",
  goal: "",
  questions: "",
  members: "",
};

interface IState {
  projectName: string;
  goal: string;
  questions: string;
  members: string;
}

export default function useCreateProject() {
  const [state, setState] = useState<IState>(initialState);
  const [errors, setErrors] = useState<IState>(initialErrors);

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
    if (!state.members) {
      errors.members = "Members are required";
    }
    if (!state.questions) {
      errors.questions = "Questions are required";
    }

    setErrors(errors);
    return (
      errors.projectName || errors.goal || errors.members || errors.questions
    );
  }
  async function handleSave() {
    if (isValidated()) {
      return;
    }

    const payload = {
      name: state.projectName,
      goal: state.goal,
      questions: state.questions,
      members: state.members,
    };
    const res = await fetch(baseApiUrl + userEndPoints.me, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Token " + localStorage.getItem("token"),
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (data) {
      alert("Account Updated Successfully");
    }
  }

  return { state, handleChange, handleSave, errors };
}
