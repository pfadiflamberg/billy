import { configureStore, combineReducers } from "@reduxjs/toolkit";

function counter(state = 0, action: string) {
  switch (action) {
    case "INCREMENT":
      return state + 1;
    case "DECREMENT":
      return state - 1;
    default:
      return state;
  }
}

const rootReducer = combineReducers({
  counter,
});

const store = configureStore({
  reducer: rootReducer,
});

export default store;
