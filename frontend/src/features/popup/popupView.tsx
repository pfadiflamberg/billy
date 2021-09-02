import { useAppDispatch, useAppSelector } from "../../app/hooks";
import { clearPopups, selectPopups, Popup } from "./popupSlice";
import { Modal, ListGroup } from 'react-bootstrap';

export function PopupView() {

    const dispatch = useAppDispatch();
    const popups = useAppSelector(selectPopups);

    let hasErrors = 0 < popups.length;

    return (
        <Modal show={hasErrors} onHide={() => dispatch(clearPopups())}>
            {hasErrors &&
                <div>
                    <Modal.Header closeButton>
                        <Modal.Title>{popups[0].title}</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        {popups[0].description}
                        <ListGroup>
                            {popups[0].details && popups[0].details.map((err: Popup) => {
                                return (
                                    <ListGroup.Item>{err.description + " "}
                                        {err.link &&
                                            <a target="_blank" rel="noreferrer" href={err.link}>view</a>
                                        }
                                    </ListGroup.Item>)
                            })}
                        </ListGroup>
                    </Modal.Body>
                </div>
            }
        </Modal>
    )

}