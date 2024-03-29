import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { selectPopups, removePopup, Popup } from "./popupSlice";
import { Button, ListGroup, Modal } from 'react-bootstrap';
import { InvoiceListView } from "../invoice/invoiceListView";

export function PopupView() {

    const dispatch = useAppDispatch();
    const popups = useAppSelector(selectPopups);

    var index = popups.length - 1;
    var popup = popups[index];

    return (
        <Modal show={popup !== undefined} onHide={() => dispatch(removePopup(index))}>
            {popup &&
                <div>
                    <Modal.Header closeButton>
                        <Modal.Title>{popup.title}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {popup.description}
                        {popup.details && popup.details_type === 'ERROR' &&
                            <ListGroup>
                                {popup.details.map((err: Popup) => {
                                    return (
                                        <ListGroup.Item>{err.description + " "}
                                            {err.link &&
                                                <a target="_blank" rel="noreferrer" href={err.link}>view</a>
                                            }
                                        </ListGroup.Item>)
                                })}
                            </ListGroup>
                        }
                        {popup.details && popup.details_type === 'INVOICE_NAME' &&
                            <InvoiceListView with_names={popup.details} />
                        }
                    </Modal.Body>
                    {popup.action &&
                        <Modal.Footer>
                            <Button onClick={(e) => {
                                popup.action.func(dispatch);
                                dispatch(removePopup(index));
                            }}>{popup.action.label}</Button>
                        </Modal.Footer>
                    }
                </div>
            }
        </Modal>
    )

}