import React, {useEffect} from 'react';
import {useAppDispatch, useAppSelector} from "./app/hooks";
import {selfConfigure} from "./features/backend/backendSlice";
import {BulkInvoiceList} from "./pages/BulkInvoiceList";
import {fetchBulks} from "./features/bulk/bulkSlice";
import {ErrorView} from "./features/error/errorView";
import {showCreateBulkView} from "./features/bulk/bulkSlice";
import {Navbar, Nav, Button} from 'react-bootstrap';
import {BulkCreateView} from "./features/bulk/bulkCreateView";
import {selectAuthenticatedState} from "./features/auth/authSlice";
import {AuthView} from "./features/auth/authView";

import './App.css';

function App() {

  // self configure backend
  const dispatch = useAppDispatch();
  dispatch(selfConfigure());

  useEffect(() => {
    dispatch(fetchBulks())
  })

  const authenticated: boolean = useAppSelector(selectAuthenticatedState);

  return (
    <div className="App">
        { authenticated &&
        <div>
            <Navbar bg="light" expand="lg">
                <Navbar.Brand href="#home">billy</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="ml-auto">
                        <Button onClick={e => dispatch(showCreateBulkView(true))} variant="outline-primary">New Bulk</Button>
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
            <ErrorView />
            <BulkInvoiceList />
            <BulkCreateView />
        </div>
        }
        { !authenticated &&
        <div>
            <AuthView />
        </div>
        }
    </div>
  );
}

export default App;
