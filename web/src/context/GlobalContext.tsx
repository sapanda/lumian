import { createContext, ReactNode, useReducer } from "react";
import actions from "./actions";

interface GlobalProviderProps {
  children: ReactNode;
}

interface User {
  name: string;
  email: string;
  [key: string]: object | string | number | boolean;
}

interface AppBar {
  [key: string]: object | string | number | boolean;
}

interface StateType {
  user: User;
  appBar: AppBar;
}

interface ActionPayloadType {
  [key: string]: object | string | number | boolean;
}
interface ActionType {
  // Define the action properties and their types here
  type: string;
  payload?: ActionPayloadType;
}
interface GlobalContextType {
  state: StateType;
  dispatch: React.Dispatch<ActionType>;
}

export const GlobalContext = createContext<GlobalContextType>({
  state: {
    user: {
      name: "",
      email: "",
    },
    appBar: {},
  },
  dispatch: () => null,
});

const initialState: StateType = {
  user: {
    name: "",
    email: "",
  },
  appBar: {},
};

const reducer = (state: StateType, action: ActionType) => {
  switch (action.type) {
    case actions.global.SET_USER:
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };

    // Handle different types of actions here
    default:
      return state;
  }
};

const GlobalProvider = ({ children }: GlobalProviderProps) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <GlobalContext.Provider
      value={{
        state,
        dispatch,
      }}
    >
      {children}
    </GlobalContext.Provider>
  );
};

export default GlobalProvider;
