import React from 'react';
import './App.css';

import {useAppDispatch} from "./app/hooks";
import {selfConfigure} from "./features/backend/backendSlice";
import {BulkInvoiceList} from "./pages/BulkInvoiceList";
import {ErrorView} from "./features/error/errorView";

function App() {

  // self configure backend
  const dispatch = useAppDispatch();
  dispatch(selfConfigure());

  return (
    <div className="App">
      <ErrorView />
      <BulkInvoiceList />
    </div>
  );
}

export default App;
