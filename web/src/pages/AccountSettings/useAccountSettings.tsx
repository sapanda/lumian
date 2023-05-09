import { useState } from "react";
import { baseApiUrl, userEndPoints } from "../../api/apiEndpoints";

const initialState = {
  name: "",
  email: "",
  oldPassword: "",
  newPassword: "",
};

const initialErrors = {
  name: "",
  email: "",
  oldPassword: "",
  newPassword: "",
};

interface IState {
  name: string;
  email: string;
  oldPassword: string;
  newPassword: string;
}

export default function useAccountSettings(defaultValues: IState) {
  const [state, setState] = useState<IState>({
    ...initialState,
    ...defaultValues,
  });
  const [errors, setErrors] = useState<IState>(initialErrors);

  function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = event.target;
    setState((prevState) => ({ ...prevState, [name]: value }));
    return;
  }

  function isValidated() {
    const errors = { ...initialErrors };
    if (!state.name) {
      errors.name = "Name is required";
    }
    if (!state.email) {
      errors.email = "Email is required";
    }
    if (!state.oldPassword) {
      errors.oldPassword = "Old Password is required";
    }
    if (!state.newPassword) {
      errors.newPassword = "New Password is required";
    }

    setErrors(errors);
    return (
      errors.name || errors.email || errors.oldPassword || errors.newPassword
    );
  }
  async function handleSave() {
    if (isValidated()) {
      return;
    }

    const payload = {
      email: state.email,
      name: state.name,
      password: state.newPassword,
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
