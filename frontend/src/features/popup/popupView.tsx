import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { clearPopups, selectPopups, Popup } from "./popupSlice";
import { Modal, ListGroup } from 'react-bootstrap';
import { InvoiceListView } from "../invoice/invoiceListView";

export function PopupView() {

    const dispatch = useAppDispatch();
    const popups = useAppSelector(selectPopups);

    let hasErrors = 0 < popups.length;

    var popup = popups[0];

    return (
        <Modal show={hasErrors} onHide={() => dispatch(clearPopups())}>
            {hasErrors &&
                <div>
                    <Modal.Header closeButton>
                        <Modal.Title>{popup.title}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {popup.description}
                        {popup.details && popup.details_type == 'ERROR' &&
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
                        {popup.details && popup.details_type == 'INVOICE_NAME' &&
                            <InvoiceListView with_names={popup.details} />
                        }
                    </Modal.Body>
                </div>
            }
        </Modal>
    )

}