import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import backendReducer from '../features/backend/backendSlice';
import errorReducer from '../features/error/errorSlice';
import bulkReducer from '../features/bulk/bulkSlice';
import authReducer from '../features/auth/authSlice';

export const store = configureStore({
  reducer: {
    backend: backendReducer,
    error: errorReducer,
    auth: authReducer,
    bulk: bulkReducer,
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
