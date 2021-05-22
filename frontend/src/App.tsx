import React from 'react';
import './App.css';

import {useAppDispatch} from "./app/hooks";
import {selfConfigure} from "./features/backend/backendSlice";
import {BulkInvoiceList} from "./pages/BulkInvoiceList";
import {ErrorView} from "./features/error/errorView";
import {createNewBulk} from "./features/bulk/bulkSlice";
import {Navbar, Nav, Button} from 'react-bootstrap';
import {BulkCreateView} from "./features/bulk/bulkCreateView";

function App() {

  // self configure backend
  const dispatch = useAppDispatch();
  dispatch(selfConfigure());

  return (
    <div className="App">
        <Navbar bg="light" expand="lg">
            <Navbar.Brand href="#home">billy</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="ml-auto">
                    <Button onClick={e => dispatch(createNewBulk())} variant="outline-success">New Bulk</Button>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
      <ErrorView />
      <BulkInvoiceList />
      <BulkCreateView />
    </div>
  );
}

export default App;
