import { useState } from "react";
import { useGetMeQuery, useUpdateMeMutation } from "../../api/userApi";

const initialState = {
  name: "",
  email: "",
  oldPassword: "",
  newPassword: "",
  bot_name: "",
};

const initialErrors = {
  ...initialState,
};

interface IState {
  name: string;
  email: string;
  oldPassword: string;
  newPassword: string;
  bot_name: string;
}

export default function useAccountSettings(defaultValues: IState) {
  const { data: user } = useGetMeQuery();
  const { mutate: updateMe } = useUpdateMeMutation();

  const [state, setState] = useState<IState>({
    ...initialState,
    ...defaultValues,
    ...(user || {}),
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
    if (!state.bot_name) {
      errors.bot_name = "Bot Name is required";
    }
    if (state.newPassword) {
      if (!state.oldPassword) {
        errors.oldPassword = "Old Password is required";
      }
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
      bot_name: state.bot_name,
      password: state.newPassword ? state.newPassword : undefined,
    };
    updateMe(payload);
  }

  return { state, handleChange, handleSave, errors };
}
