import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import backendReducer from '../features/backend/backendSlice';
import errorReducer from '../features/error/errorSlice';

export const store = configureStore({
  reducer: {
    backend: backendReducer,
    error: errorReducer,
  },
});

export type AppDispatch = typeof store.dispatch;
export type RootState = ReturnType<typeof store.getState>;
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>;
