import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import backendReducer from '../features/backend/backendSlice';

export const store = configureStore({
  reducer: {
    backend: backendReducer,
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
