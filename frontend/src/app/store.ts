import { configureStore, ThunkAction, Action } from '@reduxjs/toolkit';
import backendReducer from '../features/backend/backendSlice';
import errorReducer from '../features/error/errorSlice';
import authReducer from '../features/auth/authSlice';
import bulkReducer from '../features/bulk/bulkSlice';
import invoiceReducer from '../features/invoice/invoiceSlice';

export const store = configureStore({
  reducer: {
    backend: backendReducer,
    error: errorReducer,
    auth: authReducer,
    bulk: bulkReducer,
    invoice: invoiceReducer,
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
